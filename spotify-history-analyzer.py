# -*- coding: utf-8 -*-

# import built-in modules
import argparse
import logging
import os
import time

# import third-party modules
import pandas as pd
import matplotlib.pyplot as plt

# import your own module

VERSION = "0.1"
APP_NAME = "Spotify History Analyzer"
APP_DESCRIPTION = "Detailed analysis of data contained in Spotify Streaming History files."

OUTPUT_FOLDER = "output/"


def parse_argv() -> dict:
    """
    Parse command-line arguments into a dict.
    """
    arg_parser = argparse.ArgumentParser(prog=APP_NAME, description=APP_DESCRIPTION)
    arg_parser.add_argument("streaming_history_folder", type=str,
                            help="Path to folder containing Spotify Streaming History")
    # arg_parser.add_argument("-o", "--output", type=str, required=False,
    #                         dest="output",
    #                         help="output .csv file")
    arg_parser.add_argument("-d", "--debug", action="store_true", required=False, default=False,
                            help="display debug logging lines")
    args = arg_parser.parse_args()
    args_dict = vars(args)
    return args_dict


# Script starts here
if __name__ == '__main__':
    script_start_time = time.time()

    # Parse command line arguments
    args = parse_argv()

    # Set-up logging
    if args["debug"]:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    logging.basicConfig(level=logging_level)

    logging.info(f"{APP_NAME} v{VERSION}")

    # -----------------------------------
    # - Load the Streaming History Data -
    # -----------------------------------
    logging.info(f"Looking for files in {args['streaming_history_folder']}")

    df = None

    for filename in os.listdir(args["streaming_history_folder"]):
        if "endsong" in filename:
            filepath = os.path.join(args["streaming_history_folder"], filename)
            logging.info(f"\tFile found: {filepath}")

            new_df = pd.read_json(filepath,
                                  dtype={"ts": "datetime64[ns]"})

            if df is None:
                df = new_df
            else:
                df = pd.concat([df, new_df])

    df = df.sort_values("ts")

    logging.info(f"Successfully read {len(df)} entries.")

    # ----------------------------------
    # - Analyze Streaming History Data -
    # ----------------------------------

    logging.info("Analyzing Streaming History Data")

    first_year = df.ts.min().year
    last_year = df.ts.max().year

    # ----------
    # Total streaming time
    logging.info("Total streaming time")

    logging.info("\tTotal per year")
    time_per_year = df.groupby(pd.Grouper(key="ts", freq="Y"))["ms_played"].sum().divide(1000 * 60)
    plt.clf()
    time_per_year.plot.bar()
    plt.title("Total time per year")
    plt.ylabel("Streaming time (minutes)")
    plt.xlabel("Year")
    plt.xticks(ticks=plt.xticks()[0], labels=[d.year for d in time_per_year.index])
    plt.grid(True, axis="y")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_FOLDER + "time_per_year.png")

    logging.info("\tTotal per month over all years")
    time_per_month = df.groupby(pd.Grouper(key="ts", freq="M"))["ms_played"].sum().divide(1000 * 60)
    plt.clf()
    for year in range(first_year, last_year+1):
        sdf = time_per_month[time_per_month.index.year == year]
        plt.plot(sdf.index.month, sdf, label=str(year))
    plt.title("Total time per month")
    plt.ylabel("Streaming time (minutes)")
    plt.xlabel("Month")
    plt.legend()
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig(OUTPUT_FOLDER + "time_per_month.png")

    logging.info("\tTotal per hour of the day")
    time_per_hour = df.groupby(df.ts.dt.hour)["ms_played"].sum().divide(1000 * 60)
    plt.clf()
    time_per_hour.plot.bar()
    plt.title("Total time per hour of the day")
    plt.ylabel("Streaming time (minutes)")
    plt.xlabel("Hour (UTC)")
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig(OUTPUT_FOLDER + "time_per_hour.png")

    logging.info("\tTotal per hour of the day for each year")

    plt.clf()
    for year in range(first_year, last_year+1):
        sdf = df[df.ts.dt.year == year]
        time_per_hour_per_year = sdf.groupby(sdf.ts.dt.hour)["ms_played"].sum().divide(1000 * 60)
        plt.plot(time_per_hour_per_year.index, time_per_hour_per_year, label=str(year))
    plt.title("Total time per hour of the day")
    plt.ylabel("Streaming time (minutes)")
    plt.xlabel("Hour (UTC)")
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.legend()
    plt.savefig(OUTPUT_FOLDER + "time_per_hour_for_each_year.png")

    # ----------
    # Time per artist
    logging.info("Time per artist")

    logging.info("\tAll time")
    time_per_artist = df.groupby("master_metadata_album_artist_name")["ms_played"].sum().sort_values(ascending=False).divide(1000*60)

    plt.clf()
    time_per_artist.iloc[:20].plot.bar()
    plt.title("Time per artist")
    plt.ylabel("Streaming time (minutes)")
    plt.xlabel("")
    plt.grid(True, axis="y")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_FOLDER + "time_per_artist.png")

    for year in range(first_year, last_year + 1):
        logging.info(f"\t{year}")

        # Per year
        df_per_year = df[df["ts"].dt.year == year]
        time_per_artist_per_year = df_per_year.groupby("master_metadata_album_artist_name")["ms_played"].sum().sort_values(ascending=False).divide(1000*60)

        plt.clf()
        time_per_artist_per_year.iloc[:20].plot.bar()
        plt.title(f"Time per artist in {year}")
        plt.ylabel("Streaming time (minutes)")
        plt.xlabel("")
        plt.grid(True, axis="y")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(OUTPUT_FOLDER + f"time_per_artist_in_{year}.png")

        # Per month
        for month in range(1, 12 + 1):
            df_per_month = df_per_year[df_per_year["ts"].dt.month == month]
            time_per_artist_per_month = df_per_month.groupby("master_metadata_album_artist_name")["ms_played"].sum().sort_values(ascending=False).divide(1000*60)

            if not time_per_artist_per_month.empty:
                plt.clf()
                time_per_artist_per_month.iloc[:20].plot.bar()
                plt.title(f"Time per artist in {year}-{month}")
                plt.ylabel("Streaming time (minutes)")
                plt.xlabel("")
                plt.grid(True, axis="y")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                plt.savefig(OUTPUT_FOLDER + f"time_per_artist_in_{year}-{month}.png")

    # ----------
    # Nb of streams per artist
    logging.info("Nb of streams per artist")

    logging.info("\tAll time")
    streams_per_artist = df["master_metadata_album_artist_name"].value_counts()

    plt.clf()
    streams_per_artist.iloc[:20].plot.bar()
    plt.title("Nb of streams per artist")
    plt.grid(True, axis="y")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_FOLDER + "nbstreams_per_artist.png")

    for year in range(first_year, last_year+1):
        logging.info(f"\t{year}")

        # Per year
        df_per_year = df[df["ts"].dt.year == year]
        streams_per_artist_per_year = df_per_year["master_metadata_album_artist_name"].value_counts()

        plt.clf()
        streams_per_artist_per_year.iloc[:20].plot.bar()
        plt.title(f"Nb of streams per artist in {year}")
        plt.grid(True, axis="y")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(OUTPUT_FOLDER + f"nbstreams_per_artist_in_{year}.png")

        # Per month
        for month in range(1, 12+1):
            df_per_month = df_per_year[df_per_year["ts"].dt.month == month]
            streams_per_artist_per_month = df_per_month["master_metadata_album_artist_name"].value_counts()

            if not streams_per_artist_per_month.empty:
                plt.clf()
                streams_per_artist_per_month.iloc[:20].plot.bar()
                plt.title(f"Nb of streams per artist in {year}-{month}")
                plt.grid(True, axis="y")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                plt.savefig(OUTPUT_FOLDER + f"nbstreams_per_artist_in_{year}-{month}.png")

    # ----------
    # Nb of streams per album
    logging.info("Nb of streams per album")

    logging.info("\tAll time")
    streams_per_album = df["master_metadata_album_album_name"].value_counts()

    plt.clf()
    streams_per_album.iloc[:20].plot.bar()
    plt.title("Nb of streams per album")
    plt.grid(True, axis="y")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_FOLDER + "nbstreams_per_album.png")

    for year in range(first_year, last_year+1):
        logging.info(f"\t{year}")

        # Per year
        df_per_year = df[df["ts"].dt.year == year]
        streams_per_album_per_year = df_per_year["master_metadata_album_album_name"].value_counts()

        plt.clf()
        streams_per_album_per_year.iloc[:20].plot.bar()
        plt.title(f"Nb of streams per album in {year}")
        plt.grid(True, axis="y")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(OUTPUT_FOLDER + f"nbstreams_per_album_in_{year}.png")

        # Per month
        for month in range(1, 12+1):
            df_per_month = df_per_year[df_per_year["ts"].dt.month == month]
            streams_per_album_per_month = df_per_month["master_metadata_album_album_name"].value_counts()

            if not streams_per_album_per_month.empty:
                plt.clf()
                streams_per_album_per_month.iloc[:20].plot.bar()
                plt.title(f"Nb of streams per album in {year}-{month}")
                plt.grid(True, axis="y")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                plt.savefig(OUTPUT_FOLDER + f"nbstreams_per_album_in_{year}-{month}.png")

    # ----------
    # Nb of streams per track
    logging.info("Nb of streams per track")

    logging.info("\tAll time")
    streams_per_track = df["master_metadata_track_name"].value_counts()

    plt.clf()
    streams_per_track.iloc[:20].plot.bar()
    plt.title("Nb of streams per track")
    plt.grid(True, axis="y")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_FOLDER + "nbstreams_per_track.png")

    for year in range(first_year, last_year + 1):
        logging.info(f"\t{year}")

        # Per year
        df_per_year = df[df["ts"].dt.year == year]
        streams_per_track_per_year = df_per_year["master_metadata_track_name"].value_counts()

        plt.clf()
        streams_per_track_per_year.iloc[:20].plot.bar()
        plt.title(f"Nb of streams per track in {year}")
        plt.grid(True, axis="y")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(OUTPUT_FOLDER + f"nbstreams_per_track_in_{year}.png")

        # Per month
        for month in range(1, 12 + 1):
            df_per_month = df_per_year[df_per_year["ts"].dt.month == month]
            streams_per_track_per_month = df_per_month["master_metadata_track_name"].value_counts()

            if not streams_per_track_per_month.empty:
                plt.clf()
                streams_per_track_per_month.iloc[:20].plot.bar()
                plt.title(f"Nb of streams per track in {year}-{month}")
                plt.grid(True, axis="y")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                plt.savefig(OUTPUT_FOLDER + f"nbstreams_per_track_in_{year}-{month}.png")

    script_end_time = time.time()
    logging.info("End of script.")
    logging.info(f"Executed in {script_end_time-script_start_time} seconds.")
