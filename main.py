import sys
import os
import sqlite3
import subprocess
import json

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTableWidgetItem, QPushButton, QLineEdit, QMessageBox,
    QFileDialog, QHBoxLayout, QHeaderView, QSplashScreen, QVBoxLayout, QLabel, QComboBox, QAction, QMenuBar
)
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont, QPainter
from PyQt5.QtGui import QIntValidator

from db_ui import Ui_Form  
from search import searchDatabase  


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, 'db/components.db')
DATA_FILE = os.path.join(BASE_DIR, 'data/data.json')
BACKUP_FILE = os.path.join(BASE_DIR, 'db/backup.db')

class MainWindow(QMainWindow): 
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()  
        self.ui.setupUi(self)  

        # Set the window title and size
        self.setWindowTitle("LabParts Micro")
        self.resize(1600, 900) 

        # Disable window maximization
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        # Set up a vertical layout for the entire window
        main_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        # Create the menu bar
        self.setup_menu()

        # Search section (search field + search button)
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.ui.searchField)
        search_layout.addWidget(self.ui.searchButton)
        main_layout.addLayout(search_layout)

        # Add the parts table widget to the layout
        main_layout.addWidget(self.ui.partsTable)

        # Center the "Add Component" and "Save Database" buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch() 
        button_layout.addWidget(self.ui.addComponentButton)
        button_layout.addWidget(self.ui.saveDatabaseButton)
        button_layout.addStretch()  
        main_layout.addLayout(button_layout)

        # Footer layout 
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        footer_label = QLabel("LabParts - Version 0.0.1 | © 2024")
        footer_label.setStyleSheet("color: #888888; font-size: 12px;")  
        footer_layout.addWidget(footer_label)
        footer_layout.addStretch()
        main_layout.addLayout(footer_layout)

        # Set up column behaviors for the parts table
        self.setup_table_columns()

        # Connect the buttons to their respective functions
        self.setup_actions()

        # Load data from JSON file
        self.load_data()

        # Open the database connection
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.cursor = self.conn.cursor()
        self.initDB()
        self.loadDatabase()

    def setup_menu(self):
        """Set up the menu bar with Backup and Restore options."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu('File')

        # Backup Database action
        backup_action = QAction('Backup Database', self)
        backup_action.triggered.connect(self.backupDatabase)
        file_menu.addAction(backup_action)

        # Restore Database action
        restore_action = QAction('Restore Database', self)
        restore_action.triggered.connect(self.restoreDatabase)
        file_menu.addAction(restore_action)

        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def setup_table_columns(self):
        """Set up the table columns and their behaviors."""
        # Stretch the Description column (column index 4) more than the other columns
        header = self.ui.partsTable.horizontalHeader()
        header.setStretchLastSection(False) 
        header.setSectionResizeMode(4, QHeaderView.Stretch)  

        # Optionally, make other columns fixed or adjust as needed
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID column auto-resize
        header.setSectionResizeMode(1, QHeaderView.Interactive)  # CUS ID column auto-resize
        header.setSectionResizeMode(2, QHeaderView.Interactive)  # Type column auto-resize
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Part column auto-resize
        header.setSectionResizeMode(5, QHeaderView.Interactive)  # Footprint column auto-resize
        header.setSectionResizeMode(6, QHeaderView.Interactive)  # Stock column auto-resize
        header.setSectionResizeMode(7, QHeaderView.Interactive)  # Allow manual resizing for "Datasheet" column
        header.setSectionResizeMode(8, QHeaderView.Interactive)  # Allow manual resizing for "Delete" column
        header.setSectionResizeMode(9, QHeaderView.Interactive)  # Datasheet path auto-resize

        # Set specific widths for columns
        self.ui.partsTable.setColumnWidth(1, 75)  # "CUSID" column width
        self.ui.partsTable.setColumnWidth(2, 130)  # "Type" column width
        self.ui.partsTable.setColumnWidth(5, 130)  # "Footprint" column width
        self.ui.partsTable.setColumnWidth(6, 80)  # "Datasheet" column width
        self.ui.partsTable.setColumnWidth(7, 200)  # "Datasheet" column width
        self.ui.partsTable.setColumnWidth(8, 150)  # "Delete" column width
        self.ui.partsTable.setColumnWidth(9, 100)  # "Datasheet Path" column width

        # Set larger row heights
        self.ui.partsTable.verticalHeader().setDefaultSectionSize(50)  

        # Hide the Datasheet Path column
        self.ui.partsTable.setColumnHidden(9, True)

    def setup_actions(self):
        """Connect buttons to their respective functions"""
        self.ui.addComponentButton.clicked.connect(self.add_component)
        self.ui.saveDatabaseButton.clicked.connect(self.saveDatabase)
        self.ui.searchButton.clicked.connect(self.perform_search) 

    def backupDatabase(self):
        """Backup the current database to a backup file."""
        try:
            if os.path.exists(DATABASE_FILE):
                # Copy the database file to a backup
                with open(DATABASE_FILE, 'rb') as db_file:
                    with open(BACKUP_FILE, 'wb') as backup_file:
                        backup_file.write(db_file.read())
                QMessageBox.information(self, "Backup Successful", "Database backup created successfully!")
            else:
                QMessageBox.warning(self, "Backup Failed", "No database file found to backup.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while creating backup: {str(e)}")

    def restoreDatabase(self):
        """Restore the database from a backup file."""
        try:
            if os.path.exists(BACKUP_FILE):
                # Replace the current database with the backup
                with open(BACKUP_FILE, 'rb') as backup_file:
                    with open(DATABASE_FILE, 'wb') as db_file:
                        db_file.write(backup_file.read())
                QMessageBox.information(self, "Restore Successful", "Database restored from backup successfully!")
                # Reload the database in the UI
                self.loadDatabase()
            else:
                QMessageBox.warning(self, "Restore Failed", "No backup file found to restore from.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while restoring from backup: {str(e)}")



    def perform_search(self):
        """Execute the search operation using the imported searchDatabase function"""
        search_term = self.ui.searchField.text().strip()
        searchDatabase(self, self.conn, search_term) 


    def initDB(self):
        """Create the components table if it doesn't exist"""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cus_id TEXT,
            type TEXT,
            part TEXT,
            description TEXT,
            footprint TEXT,
            stock INTEGER,
            datasheetpath TEXT
        )''')
        self.conn.commit()

    def loadDatabase(self):
        """Load components from the SQLite database into the table"""
        self.ui.partsTable.setRowCount(0)  
        self.cursor.execute("SELECT id, cus_id, type, part, description, footprint, stock, datasheetpath FROM components")
        rows = self.cursor.fetchall()

        for row_data in rows:
            row_pos = self.ui.partsTable.rowCount()
            self.ui.partsTable.insertRow(row_pos)

            for column, value in enumerate(row_data):
                if column == 6:  # Stock column (editable)
                    stock_input = QLineEdit()
                    stock_input.setValidator(QIntValidator())
                    stock_input.setText(str(value))
                    self.ui.partsTable.setCellWidget(row_pos, column, stock_input)
                elif column == 0:  # ID column (non-editable)
                    id_item = QTableWidgetItem(str(value))
                    id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) 
                    self.ui.partsTable.setItem(row_pos, column, id_item)
                elif column == 7:  # Datasheet path column (read-only)
                    # Store the datasheet path in the Datasheet Path column (column 9)
                    datasheet_path_item = QTableWidgetItem(str(value))
                    self.ui.partsTable.setItem(row_pos, 9, datasheet_path_item)
                elif column == 5:  # Footprint column (QComboBox)
                    combo = QComboBox()
                    combo.addItems(self.footprints)  # Use the loaded footprints
                    combo.setEditable(True)  # Allow users to type their own value
                    combo.setCurrentText(value)  # Set the current value to what's in the database
                    self.ui.partsTable.setCellWidget(row_pos, column, combo)
                elif column == 2:  # Type column (QComboBox)
                    type_combo = QComboBox()
                    type_combo.addItems(self.types)  # Use the loaded types
                    type_combo.setEditable(True)  # Allow users to type their own value
                    type_combo.setCurrentText(value)  # Set the current value to what's in the database
                    self.ui.partsTable.setCellWidget(row_pos, column, type_combo)
                else:
                    self.ui.partsTable.setItem(row_pos, column, QTableWidgetItem(str(value)))

            # Add Datasheet buttons in the Datasheet column (column 7)
            add_datasheet_button = QPushButton('Add')
            view_datasheet_button = QPushButton('View')
            add_datasheet_button.clicked.connect(lambda _, r=row_pos: self.link_datasheet(r))
            view_datasheet_button.clicked.connect(lambda _, r=row_pos: self.view_datasheet(r))
            self.ui.partsTable.setCellWidget(row_pos, 7, self.create_button_widget(add_datasheet_button, view_datasheet_button))

            # Add Delete button in the Delete column (column 8)
            delete_button = QPushButton('Delete')
            delete_button.setObjectName('deleteButton')  # Assign the deleteButton ID for custom styling
            self.ui.partsTable.setCellWidget(row_pos, 8, self.create_button_widget(delete_button))
            delete_button.clicked.connect(lambda _, r=row_pos: self.delete_part(r))  # Capture row_pos
            self.ui.partsTable.setCellWidget(row_pos, 8, delete_button)

    def load_data(self):
        """Load types and footprints from a JSON file."""
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                self.types = data.get("types", [])
                self.footprints = data.get("footprints", [])
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"Data file '{DATA_FILE}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Error reading JSON data: {e}")
            sys.exit(1)

    def create_button_widget(self, add_button, view_button):
        """Helper function to create a widget with Add and View buttons"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(add_button)
        layout.addWidget(view_button)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        return widget


    def add_component(self):
        """Add a new component row to the table"""
        row_pos = self.ui.partsTable.rowCount()
        self.ui.partsTable.insertRow(row_pos)

        for col in range(10):  # Adjust loop to cover all 10 columns
            if col == 0:  # ID column (non-editable, auto-generated)
                id_item = QTableWidgetItem("Auto-ID")
                id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make ID column non-editable
                self.ui.partsTable.setItem(row_pos, col, id_item)

            elif col == 2:  # Type column (QComboBox)
                type_combo = QComboBox()
                type_combo.addItems(self.types)  # Use the loaded types
                type_combo.setEditable(True)  # Allow users to type their own value
                self.ui.partsTable.setCellWidget(row_pos, col, type_combo)

            elif col == 5:  # Footprint column (QComboBox)
                combo = QComboBox()
                combo.addItems(self.footprints)  # Use the loaded footprints
                combo.setEditable(True)  # Allow users to type their own value
                self.ui.partsTable.setCellWidget(row_pos, col, combo)

            elif col == 6:  # Stock column with QLineEdit
                stock_input = QLineEdit()
                stock_input.setValidator(QIntValidator())  # Ensure only integers are entered
                self.ui.partsTable.setCellWidget(row_pos, col, stock_input)
            elif col == 7:  # Datasheet buttons
                add_datasheet_button = QPushButton('Add')
                view_datasheet_button = QPushButton('View')
                add_datasheet_button.clicked.connect(lambda _, r=row_pos: self.link_datasheet(r))
                view_datasheet_button.clicked.connect(lambda _, r=row_pos: self.view_datasheet(r))
                self.ui.partsTable.setCellWidget(row_pos, 7, self.create_button_widget(add_datasheet_button, view_datasheet_button))
            elif col == 8:  # Delete button
                delete_button = QPushButton('Delete')
                delete_button.setObjectName('deleteButton')  # Assign the deleteButton ID for custom styling
                self.ui.partsTable.setCellWidget(row_pos, 8, self.create_button_widget(delete_button))  # Use the updated function here
                delete_button.clicked.connect(lambda _, r=row_pos: self.delete_part(r))
                self.ui.partsTable.setCellWidget(row_pos, 8, delete_button)
            elif col == 9:  # Datasheet Path (empty for new component)
                datasheet_path_item = QTableWidgetItem("")
                self.ui.partsTable.setItem(row_pos, col, datasheet_path_item)
            else:
                self.ui.partsTable.setItem(row_pos, col, QTableWidgetItem(""))

    def saveDatabase(self):
        """Save the table data into the SQLite database"""
        self.cursor.execute("DELETE FROM components")  # Clear current records

        for row in range(self.ui.partsTable.rowCount()):
            id_item = self.ui.partsTable.item(row, 0)
            cus_id_item = self.ui.partsTable.item(row, 1)

            # Extract type from QComboBox
            type_widget = self.ui.partsTable.cellWidget(row, 2)
            if isinstance(type_widget, QComboBox):
                type_value = type_widget.currentText()
            else:
                type_value = ""

            part_item = self.ui.partsTable.item(row, 3)
            desc_item = self.ui.partsTable.item(row, 4)

            # Extract footprint from QComboBox
            footprint_widget = self.ui.partsTable.cellWidget(row, 5)
            if isinstance(footprint_widget, QComboBox):
                footprint_value = footprint_widget.currentText()
            else:
                footprint_value = ""

            # Stock column with QLineEdit
            stock_input = self.ui.partsTable.cellWidget(row, 6)
            if stock_input and isinstance(stock_input, QLineEdit):
                stock_value = stock_input.text() if stock_input.text().isdigit() else '0'
            else:
                stock_value = '0'

            datasheet_path_item = self.ui.partsTable.item(row, 9)  # Datasheet Path is in column 9

            self.cursor.execute('''INSERT INTO components (cus_id, type, part, description, footprint, stock, datasheetpath)
                                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                (cus_id_item.text() if cus_id_item else "",
                                 type_value,
                                 part_item.text() if part_item else "",
                                 desc_item.text() if desc_item else "",
                                 footprint_value,
                                 stock_value,
                                 datasheet_path_item.text() if datasheet_path_item else ""))

        self.conn.commit()
        QMessageBox.information(self, "Database Saved", "Database saved successfully!")


    def delete_part(self, row):
        """Delete the selected part from the table and database"""
        id_item = self.ui.partsTable.item(row, 0)  # Assuming ID is in column 0 (part ID)
        if id_item:
            part_id = id_item.text()  # Get the ID of the part
            
            # Confirm deletion
            reply = QMessageBox.question(self, 'Delete Part', f"Are you sure you want to delete part ID {part_id}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # Remove the row from the table
                self.ui.partsTable.removeRow(row)

                # Delete the part from the database using its unique ID
                self.cursor.execute("DELETE FROM components WHERE id = ?", (part_id,))
                self.conn.commit()

                QMessageBox.information(self, "Part Deleted", f"Part ID {part_id} has been deleted successfully!")
            else:
                QMessageBox.information(self, "Cancelled", "Deletion cancelled.")


    def link_datasheet(self, row):
        """Attach a datasheet to the selected component and store the path in the Datasheet Path column."""
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'PDF files (*.pdf);;All Files (*)')
        if file_name:
            relative_path = os.path.relpath(file_name, BASE_DIR)
            # Store the relative path in the Datasheet Path column (column index 9)
            datasheet_path_item = self.ui.partsTable.item(row, 9)
            
            if datasheet_path_item is None:
                datasheet_path_item = QTableWidgetItem()
                self.ui.partsTable.setItem(row, 9, datasheet_path_item)
            
            # Update the path in the Datasheet Path column
            datasheet_path_item.setText(relative_path)

            # Update the database to save the path for the component with the corresponding ID
            id_item = self.ui.partsTable.item(row, 0)  # Assuming ID is in column 0
            part_id = id_item.text() if id_item else None
            
            if part_id:
                # Update the corresponding part's datasheet path in the database
                self.cursor.execute("UPDATE components SET datasheetpath = ? WHERE id = ?", (relative_path, part_id))
                self.conn.commit()


    def view_datasheet(self, row):
        """View the attached datasheet for the selected component using the path from the Datasheet Path column."""
        id_item = self.ui.partsTable.item(row, 0)  # Assuming ID is in column 0
        datasheet_path_item = self.ui.partsTable.item(row, 9)  # Datasheet Path is in column 9
        
        if id_item and datasheet_path_item:
            part_id = id_item.text()  # Get the ID
            datasheet_path = os.path.abspath(os.path.join(BASE_DIR, datasheet_path_item.text()))  # Get the datasheet path
            
            if os.path.exists(datasheet_path):
                try:
                    # Open the datasheet using SumatraPDF located in the thirdParty folder
                    pdf_viewer = os.path.join(BASE_DIR, 'thirdParty', 'SumatraPDF-3.5.2-64.exe')
                    subprocess.Popen([pdf_viewer, datasheet_path], shell=False)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not open datasheet for ID {part_id}: {e}")
            else:
                QMessageBox.warning(self, "Error", f"File not found: {datasheet_path}")
        else:
            QMessageBox.information(self, "No Datasheet", f"No datasheet linked for ID {id_item.text() if id_item else 'Unknown'}.")

    def create_button_widget(self, *buttons):
        """Helper function to create a widget with buttons centered."""
        widget = QWidget()
        layout = QHBoxLayout()  # Horizontal layout to center the buttons
        layout.addStretch()  # Add stretchable space to the left
        for button in buttons:  # Add all passed buttons (whether 1 or 2)
            layout.addWidget(button)
        layout.addStretch()  # Add stretchable space to the right
        layout.setContentsMargins(0, 0, 0, 0)  # Set no margins
        layout.setAlignment(Qt.AlignCenter)  # Center the layout content
        widget.setLayout(layout)
        return widget


def show_splash_screen(app):
    # Create a QPixmap to represent the splash screen background
    splash_pix = QPixmap(800, 400)  # Set the size of the splash screen

    # Fill the pixmap with a purple color
    splash_pix.fill(QColor("#6200ee"))  # Material purple color

    # Create a QPainter to write "LabParts" on the pixmap
    painter = QPainter(splash_pix)
    painter.setPen(QColor("white"))  # Set the text color to white
    painter.setFont(QFont('Arial', 36, QFont.Bold))  # Set font size and boldness
    painter.drawText(splash_pix.rect(), Qt.AlignCenter, "LabParts")  # Draw "LabParts" in the center
    painter.end()

    # Create the splash screen with the pixmap
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.show()

    # Process events to keep the splash screen responsive
    app.processEvents()

    # Real Tasks during Splash Screen:
    try:
        # 1. Test the Database Connection
        splash.showMessage("Testing Database Connection...", Qt.AlignBottom | Qt.AlignCenter, QColor("white"))
        app.processEvents()
        QThread.msleep(1000)  # Wait for 1 second
        conn = sqlite3.connect(DATABASE_FILE)  # Test DB connection
        conn.cursor().execute("SELECT 1")  # Simple query to ensure DB is accessible

        # 2. Verify Icon Exists
        splash.showMessage("Verifying Icons...", Qt.AlignBottom | Qt.AlignCenter, QColor("white"))
        app.processEvents()
        QThread.msleep(1000)  # Wait for 1 second
        if not os.path.exists('icons/transistor.ico'):
            raise FileNotFoundError("Icon not found: 'icons/transistor.ico'")

        # 3. Load Critical Resources
        splash.showMessage("Loading Resources...", Qt.AlignBottom | Qt.AlignCenter, QColor("white"))
        app.processEvents()
        QThread.msleep(1000)  # Wait for 1 second

        splash.showMessage("Initialization Complete!", Qt.AlignBottom | Qt.AlignCenter, QColor("white"))
        app.processEvents()
        QThread.msleep(1000)  # Wait for 1 second

    except Exception as e:
        # Show error message and terminate if a critical error occurs
        splash.showMessage(f"Error: {str(e)}", Qt.AlignBottom | Qt.AlignCenter, QColor("red"))
        app.processEvents()
        QMessageBox.critical(None, "Startup Error", f"An error occurred: {str(e)}")
        sys.exit(1)  # Exit with error

    return splash, conn  # Return the splash screen and DB connection


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icons/transistor.ico'))  # Ensure the icon path is correct

    # Show splash screen and perform real startup tasks
    splash, conn = show_splash_screen(app)

    # Load and apply the custom stylesheet
    with open(os.path.join(BASE_DIR, 'style/style.qss'), 'r') as style_file:
        app.setStyleSheet(style_file.read())

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Close splash screen once the main window is ready
    splash.finish(window)  # Call finish on the splash object

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
