#!/usr/bin/env bash
# Uploads everything to externbob
rsync --exclude 'venv/' --exclude 'venv38/' --exclude '.env' --exclude '.git/' --recursive -e 'ssh -p 2223' $HOME/screaper/ david@77.59.149.134:'~/screaper/' -v --progress

#def upload_to_davids_cluster():
#    q = "rsync "
#    q += "--exclude='{}' ".format("analysis/viz/")
#    q += "--exclude='{}' ".format("venv/")
#    q += "--exclude='{}' ".format(".env")
#    q += "--exclude='{}' ".format("data/")
#    q += "--exclude='{}' ".format(".git/")
#    q += "--exclude='{}' ".format("rust_preprocessing/")
#    q += "--recursive -e 'ssh -p {}' ".format(port_david)
#    q += "{} ".format(basepath)
#    q += " david@{}".format(ip_david)
#    q += ":{} -v --progress".format(targetpath)
#
#    print("Copying using the following command: ", q)
#    return q
#
#
#if __name__ == "__main__":
#    print("Uploading to cluster..")
#    command = upload_to_davids_cluster()
#    os.system(command)