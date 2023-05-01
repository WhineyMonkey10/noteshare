echo "Checking for config files..."
if [ -f ".env" ]; then
    echo ".env file exists, please delete it if you want to make a new one"
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

    echo "Please enter the mongoDB collection name for the notes"
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

    echo "Please enter the mongoDB collection name for the users"
    if [ -z "$6" ]; then
        read -p "User Collection: " userCollection
    else
        userCollection=$6
    fi

    echo "Please enter the mongoDB collection name for the groups"
    if [ -z "$7" ]; then
        read -p "Group Collection: " groupCollection
    else
        groupCollection=$7
    fi

    if [ -z "$8" ]; then
        echo -e "\e[32mGenerating a secret key (used for the flask app)...\e[0m"
        secretKey=$(openssl rand -hex 32)
        echo -e "\e[32mSecret key generated\e[0m"
    else
        secretKey=$8
    fi


    if [ -z "$9" ]; then
        read -p "Encrypted? (y/n): HIGHLY RECOMMENDED " encrypted
    else
        encrypted=$9
    fi

    if [ "$encrypted" = "y" ]; then
        echo -e "\e[32mGenerating an encryption key (used for sensitive info)...\e[0m"
        while [ ${#encryptionKey} -lt 32 ]; do
            random_bytes=$(openssl rand -hex 16)
            encryptionKey=$(echo -n "$random_bytes" | base64 -d | head -c 32 | base64 -w 0)
        done
        echo -e "\e[32mEncryption key generated\e[0m"
    fi



    echo "Please enter the mongoDB collection name for the global messages"

    if [ -z "${14}" ]; then
        read -p "Global message Collection: " gMessageCollection
    else
        userCollection=${14}
    fi

    echo "Stripe Details"

    echo "Please enter the Stripe publishable key"

    if [ -z "${10}" ]; then
        read -p "Stripe Publishable Key: " stripeKeyPublishable
    else
        stripeKey=${10}
    fi


    echo "Please enter the Stripe secret key"

    if [ -z "${11}" ]; then
        read -p "Stripe Secret Key: " stripeKeySecret
    else
        stripeKey=${11}
    fi

    echo "Please enter the Stripe price ID"

    if [ -z "${12}" ]; then
        read -p "Stripe Price ID: " stripePriceID
    else
        stripePriceID=${12}
    fi

    echo "Please enter the Stripe endpoint secret for the webhook"

    echo "Please enter the Stripe price ID"

    if [ -z "${13}" ]; then
        read -p "Stripe E.P: " stripeEP
    else
        stripePriceID=${13}
    fi

echo 'URI='"${uri}"'
DATABASE='"${database}"'
COLLECTION='"${collection}"'
USERNAME='"${username}"'
PASSWORD='"${password}"'
USERCOLLECTION='"${userCollection}"'
GROUPCOLLECTION='"${groupCollection}"'
SECRETKEY='"$secretKey"'
ENCRYPTIONKEY='"$encryptionKey"'
GMESSAGECOLLECTION='"${gMessageCollection}"'
PUBLISHSTRIPEKEY='"${stripeKeyPublishable}"'
SECRETSTRIPEKEY='"${stripeKeySecret}"'
STRIPEPRICEID='"${stripePriceID}"'
STRIPEENDPOINTSECRET='"${stripeEP}"'
' >> .env

echo -e "\e[32mConfig file created\e[0m"
fi