def get_checkpoint():
    try:
        with open("checkpoint.txt") as readable:
            return int(readable.read())
    except:
        return 0


def write_checkpoint(checkpoint):
    with open("checkpoint.txt", "w") as writable:
        writable.write(str(checkpoint))
        writable.write("\n")
