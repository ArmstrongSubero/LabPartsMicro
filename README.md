LabParts



LabParts is a desktop database application designed to help hobbyists and electronics enthusiasts organize and manage their electronic components effectively. With features for storing part details, managing stock, and attaching datasheets, LabParts is the ideal tool for your small lab or workshop.

Features

Database Management: Store, search, and update details about your components, including type, part number, description, and footprint.

Datasheet Viewer: Attach datasheets in PDF format and view them directly using the integrated datasheet viewer.

Stock Management: Keep track of component quantities and locations.

Wishlist: Maintain a wishlist for components you'd like to add in the future.

Backup and Restore: Backup your database to prevent data loss and restore it when needed.

Table of Contents

Installation

Usage

Wishlist Feature

Dependencies

Contributing

License

Installation

Prerequisites

Python 3.12 or higher

PyInstaller

Recommended: Set up a virtual environment to manage dependencies.

Steps to Install

Clone the repository:

git clone https://github.com/yourusername/Parts_Database.git
cd Parts_Database

Install dependencies:

pip install -r requirements.txt

Run the application:

python main.py

To create an executable (optional):

pyinstaller --onefile --windowed --icon="icons/custom_icon.ico" \
    --add-data "data;data" --add-data "db;db" --add-data "datasheets;datasheets" \
    --add-data "icons;icons" --add-data "style;style" main.py

Usage

Main Interface

Add Components: Click "Add Component" to add a new part, including its description, type, and quantity.

Search Components: Use the search field at the top to quickly locate a part by name or ID.

View Datasheet: Click "View" next to a component to open the attached datasheet (PDF) with SumatraPDF.

Backup and Restore

Access the backup and restore options from the "File" menu to keep your database secure.

Wishlist Feature

Click on the "Wishlist" button to open a separate popup window where you can add components you wish to acquire.

This feature is designed to help you keep track of missing parts for future projects.

TODO

Improve the Wishlist feature by allowing users to set priorities and estimated prices for components.

Dependencies

PyQt5: For creating the GUI.

SQLite3: For database storage.

SumatraPDF: For viewing attached datasheets.

To install the dependencies:

pip install -r requirements.txt

Contributing

Contributions are welcome! If you find a bug or want to add new features:

Fork the repository.

Create a new branch (git checkout -b feature-name).

Commit your changes (git commit -m 'Add new feature').

Push to the branch (git push origin feature-name).

Create a pull request.

License

This project is licensed under the GPLv3 License due to the inclusion of SumatraPDF. See the LICENSE file for details.

Contact

If you have any questions, feel free to contact me via GitHub or email:

GitHub: yourusername

Email: youremail@example.com

Thank you for using LabParts! If you find this project helpful, consider giving it a star on GitHub ⭐.
