echo "Checking for config files"
if [ -f "src/Database/config.json" ]; then
    echo "Database config file already exists"
else

    if [ -f "static/config.json" ]; then
        echo "Stripe config file already exists"
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

    echo "Please enter a secret key"
    if [ -z "$7" ]; then
        read -p "Secret Key: " secretKey
    else
        secretKey=$7
    fi

    if [ -z "$8" ]; then
        read -p "Encrypted? (y/n): " encrypted
    else
        encrypted=$8
    fi

    if [ "$encrypted" = "y" ]; then
        echo "Please enter the encryption key"
        if [ -z "$9" ]; then
            read -p "Encryption Key: " encryptionKey
            while [ ${#encryptionKey} -lt 32 ]; do
                echo "Encryption key must be 32 bytes long"
                read -p "Encryption Key: " encryptionKey
            done
        else
            encryptionKey=$9
        fi
    fi

    echo"Please enter the mongoDB collection name for the global messages"
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

    echo"Please enter the Stripe secret key"
    if [ -z "${11}" ]; then
        read -p "Stripe Secret Key: " stripeKeySecret
    else
        stripeKey=${11}
    fi

    echo"Please enter the Stripe price ID"
    if [ -z "${12}" ]; then
        read -p "Stripe Price ID: " stripePriceID
    else
        stripePriceID=${12}
    fi

    echo"Please enter the Stripe endpoint secret for the webhook"
    echo"Please enter the Stripe price ID"
    if [ -z "${13}" ]; then
        read -p "Stripe E.P: " stripeEP
    else
        stripePriceID=${13}
    fi

        echo "{
        \"uri\": \"$uri\",
        \"database\": \"$database\",
        \"collection\": \"$collection\",
        \"username\": \"$username\",
        \"password\": \"$password\",
        \"userCollection\": \"$userCollection\",
        \"secretKey\": \"$secretKey\",
        \"encryptionKey\": \"$encryptionKey\",
        \"gMessageCollection\": \"$gMessageCollection\"
    }" > src/Database/config.json
fi

echo "{
        \"publishStripeKey\": \"$stripeKeyPublishable\",
        \"secretStripeKey\": \"$stripeKeySecret\",
        \"stripePriceID\": \"$stripePriceID\",
        \"stripeEndpointSecret\": \"$stripeEP\",
 }" > static/config.json