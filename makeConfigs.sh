echo "Checking for config files"
if [ -f "src/Database/config.json" ]; then
    echo "Database config file already exists"
else
    echo "Database config file does not exist"
    echo "Creating Database config file"
    echo "Making config files for Database"

    echo "Please enter the mongoDB URI"
    if [ -z "$1" ]; then
        read -p "URI: " uri
    else
        uri=$1
    fi

    echo "Please enter the mongoDB database name"
    if [ -z "$2" ]; then
        read -p "Database: " database
    else
        database=$2
    fi

    echo "Please enter the mongoDB collection name"
    if [ -z "$3" ]; then
        read -p "Collection: " collection
    else
        collection=$3
    fi

    echo "Please enter the mongoDB username"
    if [ -z "$4" ]; then
        read -p "Username: " username
    else
        username=$4
    fi

    echo "Please enter the mongoDB password"
    if [ -z "$5" ]; then
        read -p "Password: " password
    else
        password=$5
    fi

    // write the config file in JSON format
    echo "{
        \"uri\": \"$uri\",
        \"database\": \"$database\",
        \"collection\": \"$collection\",
        \"username\": \"$username\",
        \"password\": \"$password\"
    }" > src/Database/config.json
fi




