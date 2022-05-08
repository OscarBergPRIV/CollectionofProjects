import gin
import logging
from absl import app, flags
import wandb

from train import Trainer
from evaluation.eval import evaluate
from input_pipeline import datasets
from utils import utils_params, utils_misc
from models.architectures import vgg_like, inception

FLAGS = flags.FLAGS
flags.DEFINE_boolean('train', True, 'Specify whether to train or evaluate a model.')


def main(argv):

    # generate folder structures
    run_paths = utils_params.gen_run_folder()

    # set loggers
    utils_misc.set_loggers(run_paths['path_logs_train'], logging.INFO)

    # gin-config
    gin.parse_config_files_and_bindings(['configs/config.gin'], [])
    utils_params.save_config(run_paths['path_gin'], gin.config_str())

    # setup import gin
import logging
from absl import app, flags
import wandb

from train import Trainer
from evaluation.eval import evaluate
from input_pipeline import datasets
from utils import utils_params, utils_misc
from models.architectures import vgg_like, inception

FLAGS = flags.FLAGS
flags.DEFINE_boolean('train', True, 'Specify whether to train or evaluate a model.')


def main(argv):

    # generate folder structures
    run_paths = utils_params.gen_run_folder()

    # set loggers
    utils_misc.set_loggers(run_paths['path_logs_train'], logging.INFO)

    # gin-config
    gin.parse_config_files_and_bindings(['configs/config.gin'], [])
    utils_params.save_config(run_paths['path_gin'], gin.config_str())

    # setup wandb
    wandb.init(project='idrid', name=run_paths['path_model_id'],
               config=utils_params.gin_config_to_readable_dictionary(gin.config._CONFIG))

    # setup pipeline
    ds_train, ds_val, ds_test, ds_info = datasets.load()

    # model
    model = vgg_like(input_shape=ds_info["shape"],
                     input_mean_shape=ds_info["mean_shape"],
                     n_classes=ds_info["num_classes"])

    # Uncomment following lines to train inception model
    # model = inception(input_shape=ds_info["shape"],
    #                   input_mean_shape=ds_info["mean_shape"])

    if FLAGS.train:
        logging.info("Calling trainer")
        trainer = Trainer(model, ds_train, ds_val, ds_info, run_paths)
        for _ in trainer.train():
            continue
    else:
        checkpoint = 10
        evaluate(model,
                 checkpoint,
                 ds_test,
                 ds_info,
                 run_paths)


if __name__ == "__main__":
    app.run(main)
wandb
    wandb.init(project='idrid', name=run_paths['path_model_id'],
               config=utils_params.gin_config_to_readable_dictionary(gin.config._CONFIG))

    # setup pipeline
    ds_train, ds_val, ds_test, ds_info = datasets.load()

    # model
    model = vgg_like(input_shape=ds_info["shape"],
                     input_mean_shape=ds_info["mean_shape"],
                     n_classes=ds_info["num_classes"])

    # Uncomment following lines to train inception model
    # model = inception(input_shape=ds_info["shape"],
    #                   input_mean_shape=ds_info["mean_shape"])

    if FLAGS.train:
        logging.info("Calling trainer")
        trainer = Trainer(model, ds_train, ds_val, ds_info, run_paths)
        for _ in trainer.train():
            continue
    else:
        checkpoint = 10
        evaluate(model,
                 checkpoint,
                 ds_test,
                 ds_info,
                 run_paths)


if __name__ == "__main__":
    app.run(main)
