import wandb
import gin
import tensorflow as tf
import logging
from evaluation.metrics import ConfusionMatrix
import datetime
import os


@gin.configurable
class Trainer(object):
    def __init__(self, model, ds_train, ds_val, ds_info, run_paths, total_steps, log_interval, ckpt_interval):

        tf.print(model.summary())

        # Loss objective
        self.loss_object = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
        self.optimizer = tf.keras.optimizers.Adam()

        # Metrics
        self.train_loss = tf.keras.metrics.Mean(name='train_loss')
        self.train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='train_accuracy')
        self.train_precision = tf.keras.metrics.Precision(name='train_precision')
        self.train_recall = tf.keras.metrics.Recall(name='train_recall')
        self.train_auc = tf.keras.metrics.AUC(name='train_AUC')
        self.train_prc = tf.keras.metrics.AUC(name='train_PRC', curve='PR')
        self.train_f1_score = 0
        self.train_fn = tf.keras.metrics.FalseNegatives(name='train_fn')
        self.train_fp = tf.keras.metrics.FalsePositives(name='train_fp')
        self.train_tp = tf.keras.metrics.TruePositives(name='train_tp')
        self.train_tn = tf.keras.metrics.TrueNegatives(name='train_tn')

        self.test_loss = tf.keras.metrics.Mean(name='test_loss')
        self.test_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='test_accuracy')
        self.test_precision = tf.keras.metrics.Precision(name='test_precision')
        self.test_recall = tf.keras.metrics.Recall(name='test_recall')
        self.test_auc = tf.keras.metrics.AUC(name='test_AUC')
        self.test_prc = tf.keras.metrics.AUC(name='test_PRC', curve='PR')
        self.test_f1_score = 0
        self.test_fn = tf.keras.metrics.FalseNegatives(name='test_fn')
        self.test_fp = tf.keras.metrics.FalsePositives(name='test_fp')
        self.test_tp = tf.keras.metrics.TruePositives(name='test_tp')
        self.test_tn = tf.keras.metrics.TrueNegatives(name='test_tn')

        self.model = model
        self.ds_train = ds_train
        self.ds_val = ds_val
        self.ds_info = ds_info
        self.run_paths = run_paths
        self.total_steps = total_steps
        self.log_interval = log_interval
        self.ckpt_interval = ckpt_interval
        self.cm_train = ConfusionMatrix(ds_info["num_classes"])
        self.cm_test = ConfusionMatrix(ds_info["num_classes"])
        

        # Checkpoint Manager
        # ...
        self.ckpt = tf.train.Checkpoint(step=tf.Variable(1), optimizer=self.optimizer, net=self.model)
        self.manager = tf.train.CheckpointManager(self.ckpt, self.run_paths["path_ckpts_train"], max_to_keep=15)
        
        self.starttime = datetime.datetime.now().replace(microsecond=0)

    def train_step(self, images, blue_mean, labels):
        with tf.GradientTape() as tape:
            # training=True is only needed if there are layers with different
            # behavior during training versus inference (e.g. Dropout).
            predictions = self.model((images, blue_mean), training=True)
            loss = self.loss_object(labels, predictions)
        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
        pred = tf.math.argmax(predictions, axis=1)

        self.cm_train.update_state(y_pred=pred, y_true=labels)
        self.train_precision(labels, pred)
        self.train_recall(labels, pred)
        self.train_auc(labels, pred)
        self.train_prc(labels, pred)
        self.train_f1_score = self.cm_train.f1_score_calc(self.train_precision.result(), self.train_recall.result())
        self.train_fn(labels, pred)
        self.train_fp(labels, pred)
        self.train_tp(labels, pred)
        self.train_tn(labels, pred)

        self.train_loss(loss)
        self.train_accuracy(labels, predictions)

    def test_step(self, images, blue_mean, labels):
        # training=False is only needed if there are layers with different
        # behavior during training versus inference (e.g. Dropout).
        predictions = self.model((images, blue_mean), training=False)
        t_loss = self.loss_object(labels, predictions)
        pred = tf.math.argmax(predictions, axis=1)

        self.cm_test.update_state(y_pred=pred, y_true=labels)
        self.test_precision(labels, pred)
        self.test_recall(labels, pred)
        self.test_auc(labels, pred)
        self.test_prc(labels, pred)
        self.test_f1_score = self.cm_test.f1_score_calc(self.test_precision.result(), self.test_recall.result())
        self.test_fn(labels, pred)
        self.test_fp(labels, pred)
        self.test_tp(labels, pred)
        self.test_tn(labels, pred)

        self.test_loss(t_loss)
        self.test_accuracy(labels, predictions)

    def train(self):
        
        for idx, (images, labels, blue_mean) in enumerate(self.ds_train):

            step = idx + 1

            self.train_step(images, blue_mean, labels)

            curr_time = datetime.datetime.now().replace(microsecond=0)
            diff = curr_time

            if step % self.log_interval == 0:

                # Reset test metrics
                self.test_loss.reset_states()
                self.test_accuracy.reset_states()
                self.cm_test.reset_states()
                self.test_precision.reset_states()
                self.test_recall.reset_states()
                self.test_auc.reset_states()
                self.test_prc.reset_states()
                self.test_fn.reset_states()
                self.test_fp.reset_states()
                self.test_tp.reset_states()
                self.test_tn.reset_states()


                for (test_images, test_labels, test_blue_mean) in self.ds_val:
                    self.test_step(test_images, test_blue_mean, test_labels)

                template = 'Step {}, \nTrain: Loss: {}, Accuracy: {}, AUC: {}, PRC: {}, Precision: {},'
                template = template + ' Recall: {}, F1: {}, FP: {}, FN: {}, TP: {}, TN: {}\n' \
                                      'Test: Loss: {}, Accuracy: {}, AUC: {}, '
                template = template + 'PRC: {}, Precision: {}, Recall: {}, F1: {}, FP: {}, FN: {}, TP: {}, TN: {}'
                logging.info(template.format(step,
                                             self.train_loss.result(),
                                             self.train_accuracy.result() * 100,
                                             self.train_auc.result(),
                                             self.train_prc.result(),
                                             self.train_precision.result(),
                                             self.train_recall.result(),
                                             self.train_f1_score,
                                             self.train_fp.result(),
                                             self.train_fn.result(),
                                             self.train_tp.result(),
                                             self.train_tn.result(),
                                             self.test_loss.result(),
                                             self.test_accuracy.result() * 100,
                                             self.test_auc.result(),
                                             self.test_prc.result(),
                                             self.test_precision.result(),
                                             self.test_recall.result(),
                                             self.test_f1_score,
                                             self.test_fp.result(),
                                             self.test_fn.result(),
                                             self.test_tp.result(),
                                             self.test_tn.result()))

                # wandb logging
                wandb.log({'train_acc': self.train_accuracy.result(),
                           'train_loss': self.train_loss.result(),
                           'train_AUC': self.train_auc.result(),
                           'train_PRC': self.train_prc.result(),
                           'train_precision': self.train_precision.result(),
                           'train_recall': self.train_recall.result(),
                           'train_fp': self.train_fp.result(),
                           'train_fn': self.train_fn.result(),
                           'train_tp': self.train_tp.result(),
                           'train_tn': self.train_tn.result(),
                           'val_acc': self.test_accuracy.result(),
                           'val_loss': self.test_loss.result(),
                           'val_AUC': self.test_auc.result(),
                           'val_PRC': self.test_prc.result(),
                           'val_precision': self.test_precision.result(),
                           'val_recall': self.test_recall.result(),
                           'val_fp': self.test_fp.result(),
                           'val_fn': self.test_fn.result(),
                           'val_tp': self.test_tp.result(),
                           'val_tn': self.test_tn.result(),
                           'step': step})

                # Reset train metrics

                self.train_loss.reset_states()
                self.train_accuracy.reset_states()
                self.cm_train.reset_states()
                self.train_precision.reset_states()
                self.train_recall.reset_states()
                self.train_auc.reset_states()
                self.train_prc.reset_states()
                self.train_fn.reset_states()
                self.train_fp.reset_states()
                self.train_tp.reset_states()
                self.train_tn.reset_states()


                yield self.test_accuracy.result().numpy()

            if step % self.ckpt_interval == 0:
                logging.info(f'Saving checkpoint to {self.run_paths["path_ckpts_train"]}.')
                # Save checkpoint
                # ...
                save_path = self.manager.save()
                logging.info("Saved checkpoint for step {}: {}".format(int(self.ckpt.step), save_path))


            if step % self.total_steps == 0:
                logging.info(f'Finished training after {step} steps.')
                # Save final checkpoint
                # ...
                self.model.save(os.path.join(self.run_paths["path_ckpts_train"], 'ckpts', 'my_model'))
                save_path = self.manager.save()
                logging.info("Saved checkpoint for step {}: {}".format(int(self.ckpt.step), save_path))

                return self.test_accuracy.result().numpy()

            self.ckpt.step.assign_add(1)
