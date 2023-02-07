import os
import sys

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, "../..")

from pipeline import inputs
from pipeline import pipeline


def main():

    cfg = inputs.Config(
        years=[2017, 2018, 2019],
        assetid="users/ryangilberthamilton/forKen/BQ_FPCA",
        start_mmdd='04-01',
        end_mmdd='10-31',
        relative_orbit=4
    )

    pipeline.run(cfg)

    

if __name__ == '__main__':
    main()
