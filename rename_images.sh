echo "Directory name:"
read directory
echo "$directory"
cd "$directory"
num=0
for file in *.jpg; do
       mv "$file" "$(printf "%u" $num).jpg"
       let num=$num+1
done
