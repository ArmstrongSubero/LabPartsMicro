# LabParts

![LabParts Logo](icons/transistor.ico)

**LabParts** is a desktop database application designed to help makers and electronics enthusiasts organize and manage their electronic components effectively. With features for storing part details, managing stock, and attaching datasheets, LabParts is the ideal tool for your small lab or workshop. I made this as a simple, clean alternative to the complex and subscription based programs available. 

## Features

- **Database Management**: Store, search, and update details about your components, including type, part number, description, and footprint.
- **Datasheet Viewer**: Attach datasheets in PDF format and view them directly using the integrated datasheet viewer.
- **Stock Management**: Keep track of component quantities and locations.
- **Wishlist**: Maintain a wishlist for components you'd like to add in the future.
- **Backup and Restore**: Backup your database to prevent data loss and restore it when needed.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Wishlist Feature](#wishlist-feature)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites
- Python 3.12 or higher
- [PyInstaller](https://pyinstaller.org/)
- Recommended: Set up a virtual environment to manage dependencies.

### Steps to Install
There is a prebuilt exe for 64-bit windows in the dist folder. You can build from source as follows:

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/Parts_Database.git
    cd Parts_Database
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the application:
    ```sh
    python main.py
    ```

4. To create an executable (optional):
    ```sh
    pyinstaller --onefile --windowed --icon="icons/custom_icon.ico" \
        --add-data "data;data" --add-data "db;db" --add-data "datasheets;datasheets" \
        --add-data "icons;icons" --add-data "style;style" main.py
    ```

## Usage

### Main Interface
- **Add Components**: Click "Add Component" to add a new part, including its description, type, and quantity.
- **Search Components**: Use the search field at the top to quickly locate a part by name or ID.
- **View Datasheet**: Click "View" next to a component to open the attached datasheet (PDF) with SumatraPDF.

### Backup and Restore
- Access the backup and restore options from the "File" menu to keep your database secure.

### Wishlist Feature
- Click on the "Wishlist" button to open a separate popup window where you can add components you wish to acquire.
- This feature is designed to help you keep track of missing parts for future projects.

### TODO
- Add Wishlist feature by allowing users to set priorities and estimated prices for components.

## Dependencies

- [PyQt5](https://pypi.org/project/PyQt5/): For creating the GUI.
- [SQLite3](https://www.sqlite.org/index.html): For database storage.
- [SumatraPDF](https://www.sumatrapdfreader.org/): For viewing attached datasheets.

To install the dependencies:
```sh
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! If you find a bug or want to add new features:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a pull request.

## License

This project is licensed under the GPLv3 License due to the inclusion of SumatraPDF. See the [LICENSE](LICENSE) file for details. Its a requirement since I have sumatra bundled.

## Contact

If you have any questions, feel free to contact me via GitHub or email: 
- **GitHub**: [armstrongsubero](https://github.com/ArmstrongSubero)
- **Email**: [armstrongsubero@gmail.com](mailto:armstrongsuber@gmail.com)

---

Thank you for using **LabParts**! If you find this project helpful, consider giving it a star on GitHub ⭐.

