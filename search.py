import sqlite3
from PyQt5.QtWidgets import QLineEdit, QPushButton, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

def searchDatabase(main_window, conn, search_term):
    """Search the database for components based on the search query or load all if empty"""
    cursor = conn.cursor()
    
    try:
        # Check if the search term is empty, if so load all data
        if not search_term:
            cursor.execute("SELECT id, cus_id, type, part, description, footprint, stock, datasheetpath FROM components")
        else:
            # Perform a search based on the search term in CUS ID, Part, Description, and Type fields
            cursor.execute('''SELECT id, cus_id, type, part, description, footprint, stock, datasheetpath 
                              FROM components
                              WHERE cus_id LIKE ? OR type LIKE ? OR part LIKE ? OR description LIKE ?''',
                           (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))

        rows = cursor.fetchall()
        main_window.ui.partsTable.setRowCount(0)  # Clear the table before inserting results

        for row_data in rows:
            row_pos = main_window.ui.partsTable.rowCount()
            main_window.ui.partsTable.insertRow(row_pos)

            for column, value in enumerate(row_data):
                if column == 6:  # Stock column (editable)
                    stock_input = QLineEdit()
                    stock_input.setValidator(QIntValidator())  # Ensure only integers are allowed
                    stock_input.setText(str(value))
                    main_window.ui.partsTable.setCellWidget(row_pos, column, stock_input)
                elif column == 0:  # ID column (non-editable)
                    id_item = QTableWidgetItem(str(value))
                    id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    main_window.ui.partsTable.setItem(row_pos, column, id_item)
                elif column == 7:  # Datasheet path column
                    datasheet_path_item = QTableWidgetItem(str(value))
                    main_window.ui.partsTable.setItem(row_pos, 9, datasheet_path_item)
                else:
                    main_window.ui.partsTable.setItem(row_pos, column, QTableWidgetItem(str(value)))

            # Add Datasheet buttons in the Datasheet column (column 7)
            add_datasheet_button = QPushButton('Add')
            view_datasheet_button = QPushButton('View')
            add_datasheet_button.clicked.connect(lambda _, r=row_pos: main_window.link_datasheet(r))
            view_datasheet_button.clicked.connect(lambda _, r=row_pos: main_window.view_datasheet(r))
            main_window.ui.partsTable.setCellWidget(row_pos, 7, main_window.create_button_widget(add_datasheet_button, view_datasheet_button))

            # Add Delete button in the Delete column (column 8)
            delete_button = QPushButton('Delete')
            delete_button.clicked.connect(lambda _, r=row_pos: main_window.delete_part(r))  # Capture row_pos
            main_window.ui.partsTable.setCellWidget(row_pos, 8, delete_button)

    except sqlite3.Error as e:
        # Catch SQLite database errors and display a message box or log it
        print(f"Error during search: {e}")
