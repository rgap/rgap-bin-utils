# To download files from an http directory
#
# Gotten from http://stackoverflow.com/questions/23446635/how-to-download-http-directory-with-all-files-and-sub-directories-as-they-appear
# - It will download all files and subfolders in ddd directory:
# - recursively (-r),
# - not going to upper directories, like ccc/… (-np),
# - not saving files to hostname folder (-nH),
# - but to ddd by omitting first 3 folders aaa, bbb, ccc (--cut-dirs=3)
# - excluding index.html files (-R index.html)
#
# $file is an URL

file="$1"
wget -r -np -nH --cut-dirs=3 -R index.html $file
