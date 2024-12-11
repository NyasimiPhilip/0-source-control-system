from . import data
from .parser import create_parser

def main():
    with data.change_git_dir('.'):
        parser = create_parser()
        args = parser.parse_args()
        args.func(args)

if __name__ == '__main__':
    main()