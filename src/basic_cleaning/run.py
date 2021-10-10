#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas_profiling
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

def go(args):

    logger.info('Initialising W&B')
    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    logger.info(f'Starting the cleaning process - input artifact: {args.input_artifact}')
    local_path = wandb.use_artifact(args.input_artifact).file()
    df = pd.read_csv(local_path)

    logger.info('Dropping outliers')
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    logger.info('Converting data types')
    df['last_review'] = pd.to_datetime(df['last_review'])

    logger.info(f'Saving outputs to {args.output_artifact} and sending them to W&B')
    df.to_csv(args.output_artifact, index=False)

    artifact = wandb.Artifact(
     args.output_artifact,
     type=args.output_type,
     description=args.output_description,
    )
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)

    run.finish()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help='Path to the CSV file that this component of the pipeline will clean',
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help='Path to the CSV file that we obtain as the result',
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help='Output type to be logged in W&B',
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help='Description of the output to be uploaded to W&B',
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help='Minimum valid price - properties below that value will be discarded',
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help='Maximum valid price - properties above that value will be discarded',
        required=True
    )

    args = parser.parse_args()

    go(args)
