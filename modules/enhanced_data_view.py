from modules.data_view import DataWidget
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QComboBox, QTabWidget, QFileDialog, QMessageBox,
                           QLabel, QLineEdit, QRadioButton, QButtonGroup, QTableWidget, QTableWidgetItem, QHeaderView,
                           QCheckBox, QGroupBox, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os
import json
import numpy as np

class EnhancedDataWidget(DataWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = pd.DataFrame()  # Main data storage
        self.filtered_data = pd.DataFrame()  # Filtered view
        self.init_ui()
        self.load_demo_data()  # Load some demo data initially
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Data Analysis")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Data Table Tab
        self.data_tab = QWidget()
        data_layout = QVBoxLayout(self.data_tab)
        
        # Search/filter controls
        filter_layout = QHBoxLayout()
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Tìm kiếm dữ liệu...")
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)
        
        self.column_combo = QComboBox()
        self.column_combo.addItem("All Columns")
        self.column_combo.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.column_combo)
        
        data_layout.addLayout(filter_layout)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        data_layout.addWidget(self.data_table)
        
        # Import/Export controls
        io_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("Import CSV")
        self.import_btn.clicked.connect(self.import_csv)
        io_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.export_csv)
        io_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("Clear Data")
        self.clear_btn.clicked.connect(self.clear_data)
        io_layout.addWidget(self.clear_btn)
        
        data_layout.addLayout(io_layout)
        
        # Data Visualization Tab
        self.viz_tab = QWidget()
        viz_layout = QVBoxLayout(self.viz_tab)
        
        # Chart controls in a group box
        chart_group = QGroupBox("Chart Controls")
        chart_controls = QVBoxLayout(chart_group)
        
        # Chart type selection
        chart_type_layout = QHBoxLayout()
        chart_type_layout.addWidget(QLabel("Chart Type:"))
        
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot", "Histogram"])
        self.chart_combo.currentIndexChanged.connect(self.update_chart_options)
        chart_type_layout.addWidget(self.chart_combo)
        
        chart_controls.addLayout(chart_type_layout)
        
        # Axis selections
        axis_layout = QHBoxLayout()
        
        # X-axis selection
        x_axis_layout = QVBoxLayout()
        x_axis_layout.addWidget(QLabel("X-Axis:"))
        self.x_axis_combo = QComboBox()
        x_axis_layout.addWidget(self.x_axis_combo)
        axis_layout.addLayout(x_axis_layout)
        
        # Y-axis selection
        y_axis_layout = QVBoxLayout()
        y_axis_layout.addWidget(QLabel("Y-Axis:"))
        self.y_axis_combo = QComboBox()
        y_axis_layout.addWidget(self.y_axis_combo)
        axis_layout.addLayout(y_axis_layout)
        
        chart_controls.addLayout(axis_layout)
        
        # Additional chart options
        options_layout = QHBoxLayout()
        
        self.show_grid = QCheckBox("Show Grid")
        self.show_grid.setChecked(True)
        options_layout.addWidget(self.show_grid)
        
        self.show_legend = QCheckBox("Show Legend")
        self.show_legend.setChecked(True)
        options_layout.addWidget(self.show_legend)
        
        chart_controls.addLayout(options_layout)
        
        # Generate button
        self.generate_chart_btn = QPushButton("Generate Chart")
        self.generate_chart_btn.clicked.connect(self.generate_chart)
        chart_controls.addWidget(self.generate_chart_btn)
        
        viz_layout.addWidget(chart_group)
        
        # Matplotlib figure
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        viz_layout.addWidget(self.canvas)
        
        # Export chart button
        self.export_chart_btn = QPushButton("Export Chart")
        self.export_chart_btn.clicked.connect(self.export_chart)
        viz_layout.addWidget(self.export_chart_btn)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.data_tab, "Data Table")
        self.tab_widget.addTab(self.viz_tab, "Data Visualization")
        
        layout.addWidget(self.tab_widget)
        
        # Connect tab change signal to update chart if needed
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        self.setLayout(layout)
    
    def on_tab_changed(self, index):
        """Called when tab is changed"""
        if index == 1:  # Visualization tab
            # Refresh column selection combo boxes
            self.refresh_column_combos()

    def refresh_column_combos(self):
        """Refresh column selection combo boxes based on current data"""
        if self.data.empty:
            return
            
        # Store current selections
        current_x = self.x_axis_combo.currentText() if self.x_axis_combo.count() > 0 else ""
        current_y = self.y_axis_combo.currentText() if self.y_axis_combo.count() > 0 else ""
        
        # Clear and repopulate
        self.x_axis_combo.clear()
        self.y_axis_combo.clear()
        
        # Add columns as options
        for column in self.data.columns:
            self.x_axis_combo.addItem(column)
            self.y_axis_combo.addItem(column)
            
        # Restore previous selections if possible
        if current_x and current_x in self.data.columns:
            self.x_axis_combo.setCurrentText(current_x)
        if current_y and current_y in self.data.columns:
            self.y_axis_combo.setCurrentText(current_y)
            
        # Show/hide Y-axis based on chart type
        chart_type = self.chart_combo.currentText()
        self.update_chart_options()

    def update_chart_options(self):
        """Update chart options based on chart type"""
        chart_type = self.chart_combo.currentText()
        
        # Show/hide Y-axis based on chart type
        y_vis = chart_type not in ["Pie Chart", "Histogram"]
        self.y_axis_combo.setEnabled(y_vis)
        
        # For pie chart, ensure a categorical column is recommended
        if chart_type == "Pie Chart" and not self.data.empty:
            # Find categorical columns
            categorical_cols = []
            for col in self.data.columns:
                if self.data[col].dtype == 'object' or self.data[col].nunique() < 10:
                    categorical_cols.append(col)
            
            if categorical_cols and self.x_axis_combo.currentText() not in categorical_cols:
                # Select first categorical column
                self.x_axis_combo.setCurrentText(categorical_cols[0])

    def load_demo_data(self):
        """Load demonstration data"""
        # Create a sample DataFrame
        data = {
            'Date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
            'Product': ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard', 
                      'Mouse', 'Headphones', 'Speaker', 'Charger', 'Cable'],
            'Price': [1200, 800, 500, 300, 100, 50, 80, 120, 25, 15],
            'Quantity': [5, 10, 7, 3, 15, 20, 12, 8, 30, 25],
            'Sales': [6000, 8000, 3500, 900, 1500, 1000, 960, 960, 750, 375],
            'Rating': [4.5, 4.2, 4.0, 4.3, 3.8, 3.9, 4.1, 4.0, 3.5, 3.7]
        }
        self.data = pd.DataFrame(data)
        self.filtered_data = self.data.copy()
        
        # Update UI
        self.update_table(self.data)
        self.update_column_combo()
        self.refresh_column_combos()

    def update_column_combo(self):
        """Update column combo box with current data columns"""
        self.column_combo.clear()
        self.column_combo.addItem("All Columns")
        
        if not self.data.empty:
            for column in self.data.columns:
                self.column_combo.addItem(column)

    def apply_filter(self):
        """Apply search filter to data"""
        search_text = self.filter_input.text().strip().lower()
        selected_column = self.column_combo.currentText()
        
        if self.data.empty:
            return
            
        if not search_text:
            self.filtered_data = self.data.copy()
            self.update_table(self.filtered_data)
            return
            
        if selected_column == "All Columns":
            # Search in all columns
            mask = False
            for column in self.data.columns:
                mask = mask | self.data[column].astype(str).str.lower().str.contains(search_text, na=False)
        else:
            # Search in selected column
            mask = self.data[selected_column].astype(str).str.lower().str.contains(search_text, na=False)
            
        self.filtered_data = self.data[mask]
        self.update_table(self.filtered_data)

    def update_table(self, df):
        """Update the table with the provided DataFrame"""
        self.data_table.clear()
        
        if df.empty:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            return
            
        # Set row and column count
        self.data_table.setRowCount(len(df))
        self.data_table.setColumnCount(len(df.columns))
        
        # Set header labels
        self.data_table.setHorizontalHeaderLabels(df.columns)
        
        # Populate table
        for i, (_, row) in enumerate(df.iterrows()):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, item)
                
        # Make table read-only
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)

    def import_csv(self):
        """Import data from CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import CSV File", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
            
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Check if data is valid
            if df.empty:
                QMessageBox.warning(self, "Empty Data", "The selected CSV file is empty.")
                return
                
            # Update data
            self.data = df
            self.filtered_data = df.copy()
            
            # Update UI
            self.update_table(self.data)
            self.update_column_combo()
            self.refresh_column_combos()
            
            QMessageBox.information(
                self, "Import Successful", 
                f"Successfully imported {len(df)} rows from {os.path.basename(file_path)}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error importing CSV: {str(e)}")

    def export_csv(self):
        """Export data to CSV file"""
        if self.filtered_data.empty:
            QMessageBox.warning(self, "No Data", "There is no data to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV File", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
            
        try:
            # Ensure file has .csv extension
            if not file_path.endswith('.csv'):
                file_path += '.csv'
                
            # Export the filtered data
            self.filtered_data.to_csv(file_path, index=False)
            
            QMessageBox.information(
                self, "Export Successful", 
                f"Successfully exported {len(self.filtered_data)} rows to {os.path.basename(file_path)}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting CSV: {str(e)}")
    
    def clear_data(self):
        """Clear all data"""
        if self.data.empty:
            return
            
        reply = QMessageBox.question(
            self, "Confirm Clear", 
            "Are you sure you want to clear all data?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.data = pd.DataFrame()
            self.filtered_data = pd.DataFrame()
            self.update_table(self.data)
            self.update_column_combo()
            self.figure.clear()
            self.canvas.draw()

    def generate_chart(self):
        """Generate a chart based on the selected options"""
        if self.filtered_data.empty:
            QMessageBox.warning(self, "No Data", "There is no data to visualize.")
            return
        
        # Get chart parameters
        chart_type = self.chart_combo.currentText()
        x_column = self.x_axis_combo.currentText()
        y_column = self.y_axis_combo.currentText()
        
        # Validate columns
        if x_column not in self.filtered_data.columns:
            QMessageBox.warning(self, "Invalid Column", f"Column '{x_column}' not found.")
            return
        
        if chart_type != "Pie Chart" and y_column not in self.filtered_data.columns:
            QMessageBox.warning(self, "Invalid Column", f"Column '{y_column}' not found.")
            return
        
        # Clear previous figure
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        try:
            # Create chart based on type
            if chart_type == "Bar Chart":
                self.filtered_data.plot(
                    kind='bar', 
                    x=x_column, 
                    y=y_column, 
                    legend=self.show_legend.isChecked(),
                    grid=self.show_grid.isChecked(),
                    ax=ax
                )
                plt.xticks(rotation=45, ha='right')
                
            elif chart_type == "Line Chart":
                self.filtered_data.plot(
                    kind='line', 
                    x=x_column, 
                    y=y_column, 
                    legend=self.show_legend.isChecked(),
                    grid=self.show_grid.isChecked(),
                    marker='o',
                    ax=ax
                )
                
            elif chart_type == "Pie Chart":
                # For pie chart, use value counts of the selected column
                self.filtered_data[x_column].value_counts().plot(
                    kind='pie',
                    autopct='%1.1f%%',
                    shadow=True,
                    ax=ax
                )
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                
            elif chart_type == "Scatter Plot":
                self.filtered_data.plot(
                    kind='scatter',
                    x=x_column,
                    y=y_column,
                    grid=self.show_grid.isChecked(),
                    ax=ax
                )
                
            elif chart_type == "Histogram":
                self.filtered_data[x_column].plot(
                    kind='hist',
                    bins=10,
                    grid=self.show_grid.isChecked(),
                    ax=ax
                )
                
            # Set labels and title
            ax.set_xlabel(x_column)
            if chart_type not in ["Pie Chart", "Histogram"]:
                ax.set_ylabel(y_column)
            
            ax.set_title(f"{chart_type}: {x_column}" + (f" vs {y_column}" if chart_type not in ["Pie Chart", "Histogram"] else ""))
            
            # Adjust layout and draw
            plt.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.critical(self, "Chart Error", f"Error generating chart: {str(e)}")
            self.figure.clear()
            self.canvas.draw()

    def export_chart(self):
        """Export the current chart as an image"""
        if self.figure.axes:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Chart", "", "PNG Files (*.png);;JPEG Files (*.jpg);;PDF Files (*.pdf)"
            )
            
            if file_path:
                try:
                    # Make sure it has the right extension
                    if not any(file_path.endswith(ext) for ext in ['.png', '.jpg', '.pdf']):
                        file_path += '.png'
                        
                    # Save the figure
                    self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                    
                    QMessageBox.information(
                        self, "Export Successful", 
                        f"Chart successfully exported to {os.path.basename(file_path)}"
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Error exporting chart: {str(e)}")
        else:
            QMessageBox.warning(self, "No Chart", "There is no chart to export.") 