import argparse
from .io import SPLITS
from .eda import inspect
from .experiment import train, evaluate


def main():
    parser = argparse.ArgumentParser(description="CAN-IDS learning starter (original set_01)")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("inspect", help="sample a split, save EDA summaries and plots")
    p.add_argument("--data-root", required=True)
    p.add_argument("--split", default="train_01", choices=SPLITS)
    p.add_argument("--fraction", type=float, default=0.02)
    p.add_argument("--output", default="results/figures")
    p = sub.add_parser("train", help="capture-held-out validation, save fitted models")
    p.add_argument("--data-root", required=True)
    p.add_argument("--fraction", type=float, default=0.02)
    p.add_argument("--out", default="results/metrics/validation.json")
    p.add_argument("--model-dir", default="models")
    p = sub.add_parser("evaluate", help="evaluate saved models on author-provided test splits")
    p.add_argument("--data-root", required=True)
    p.add_argument("--fraction", type=float, default=0.005)
    p.add_argument("--out", default="results/metrics/test.json")
    p.add_argument("--model-dir", default="models")
    p.add_argument("--splits", nargs="+", choices=SPLITS[1:], default=list(SPLITS[1:]))
    a = parser.parse_args()
    if a.command == "inspect":
        inspect(a.data_root, a.split, a.fraction, a.output)
    elif a.command == "train":
        train(a.data_root, a.fraction, a.out, a.model_dir)
    elif a.command == "evaluate":
        evaluate(a.data_root, a.fraction, a.out, a.model_dir, a.splits)


if __name__ == "__main__":
    main()
