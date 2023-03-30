echo "Starting setup..."
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Removing config files..."
rm -rf src/Database/config.json
rm -rf static/config.json
echo -e "\e[32mRemoved config files...\e[0m"
echo "Creating config files..."
bash makeConfigs.sh
echo -e "\e[32mCreated config files...\e[0m"
echo "Starting web server..."
python main.py
echo "Setup complete!"