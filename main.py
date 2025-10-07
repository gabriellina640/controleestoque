from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt, QDate
import sys
from datetime import datetime
from models import Product, Sale, load_data, save_data

class InventoryApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle de Estoque RTimportações")
        self.setGeometry(200, 100, 1000, 600)
        self.data = load_data()
        self.clean_sales()
        self.setup_ui()
        self.update_product_table()
        self.update_sales_table()

    # Remove vendas de produtos excluídos
    def clean_sales(self):
        active_ids = {p["id"] for p in self.data["products"]}
        self.data["sales"] = [s for s in self.data["sales"] if s["product_id"] in active_ids]
        save_data(self.data)

    # Configuração da UI
    def setup_ui(self):
        # Menu à direita
        menu_bar = self.menuBar()
        menu_bar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        menu_actions = QtWidgets.QMenu("Menu", self)
        menu_bar.addMenu(menu_actions)

        menu_actions.addAction("Adicionar Produto", self.add_product)
        menu_actions.addAction("Editar Produto", self.edit_product)
        menu_actions.addAction("Excluir Produto", self.delete_product)
        menu_actions.addAction("Registrar Venda", self.sell_product)
        menu_actions.addAction("Total Vendido", self.total_sales)
        menu_actions.addAction("Total por Período", self.total_sales_period)

        # Central com abas
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout()
        central.setLayout(layout)

        self.tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.tabs)

        # Aba Produtos
        self.tab_products = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout()
        self.tab_products.setLayout(tab_layout)
        self.tabs.addTab(self.tab_products, "Produtos")

        search_layout = QtWidgets.QHBoxLayout()
        tab_layout.addLayout(search_layout)
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Buscar produto pelo nome...")
        self.search_input.textChanged.connect(self.search_products)
        search_layout.addWidget(self.search_input)

        self.product_table = QtWidgets.QTableWidget()
        self.product_table.setColumnCount(4)
        self.product_table.setHorizontalHeaderLabels(["ID", "Nome", "Preço", "Quantidade"])
        self.product_table.horizontalHeader().setStretchLastSection(True)
        self.product_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        tab_layout.addWidget(self.product_table)

        # Aba Vendas
        self.tab_sales = QtWidgets.QWidget()
        sales_layout = QtWidgets.QVBoxLayout()
        self.tab_sales.setLayout(sales_layout)
        self.tabs.addTab(self.tab_sales, "Vendas")

        # Filtros de vendas
        filter_layout = QtWidgets.QHBoxLayout()
        sales_layout.addLayout(filter_layout)

        self.sales_search_input = QtWidgets.QLineEdit()
        self.sales_search_input.setPlaceholderText("Buscar vendas por produto...")
        self.sales_search_input.textChanged.connect(self.filter_sales)
        filter_layout.addWidget(self.sales_search_input)

        self.start_date = QtWidgets.QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.start_date)

        self.end_date = QtWidgets.QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)

        btn_filter = QtWidgets.QPushButton("Filtrar")
        btn_filter.clicked.connect(self.filter_sales)
        filter_layout.addWidget(btn_filter)

        self.sales_table = QtWidgets.QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["Produto", "Quantidade", "Total", "Data", "Produto ID"])
        self.sales_table.horizontalHeader().setStretchLastSection(True)
        self.sales_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        sales_layout.addWidget(self.sales_table)

    # Atualizações
    def update_product_table(self, filtered=None):
        products = filtered if filtered is not None else self.data["products"]
        self.product_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.product_table.setItem(row, 0, QtWidgets.QTableWidgetItem(p["id"]))
            self.product_table.setItem(row, 1, QtWidgets.QTableWidgetItem(p["name"]))
            self.product_table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"R${p['price']}"))
            self.product_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(p["quantity"])))

    def update_sales_table(self, filtered=None):
        sales = filtered if filtered is not None else self.data["sales"]
        self.sales_table.setRowCount(len(sales))
        for row, s in enumerate(sales):
            product_name = next((p["name"] for p in self.data["products"] if p["id"] == s["product_id"]), "Excluído")
            self.sales_table.setItem(row, 0, QtWidgets.QTableWidgetItem(product_name))
            self.sales_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(s["quantity_sold"])))
            self.sales_table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"R${s['total']}"))
            self.sales_table.setItem(row, 3, QtWidgets.QTableWidgetItem(datetime.fromisoformat(s["date"]).strftime("%d/%m/%Y %H:%M")))
            self.sales_table.setItem(row, 4, QtWidgets.QTableWidgetItem(s["product_id"]))

    # Busca produtos
    def search_products(self, text):
        filtered = [p for p in self.data["products"] if text.lower() in p["name"].lower()]
        self.update_product_table(filtered)

    # Filtro vendas
    def filter_sales(self):
        text = self.sales_search_input.text().lower()
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        filtered = [
            s for s in self.data["sales"]
            if start <= datetime.fromisoformat(s["date"]).date() <= end
            and text in next((p["name"].lower() for p in self.data["products"] if p["id"] == s["product_id"]), "")
        ]
        self.update_sales_table(filtered)

    # Adicionar produto
    def add_product(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Produto", "Nome do produto:")
        if not ok or not name: return
        price, ok = QtWidgets.QInputDialog.getDouble(self, "Produto", "Preço:")
        if not ok: return
        quantity, ok = QtWidgets.QInputDialog.getInt(self, "Produto", "Quantidade:")
        if not ok: return
        product_id = str(len(self.data["products"]) + 1)
        product = Product(product_id, name, price, quantity)
        self.data["products"].append(product.__dict__)
        save_data(self.data)
        self.update_product_table()

    # Editar produto
    def edit_product(self):
        selected = self.product_table.currentRow()
        if selected == -1:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um produto")
            return
        product = self.data["products"][selected]
        name, ok = QtWidgets.QInputDialog.getText(self, "Editar Produto", "Nome:", text=product["name"])
        if not ok or not name: return
        price, ok = QtWidgets.QInputDialog.getDouble(self, "Editar Produto", "Preço:", value=product["price"])
        if not ok: return
        quantity, ok = QtWidgets.QInputDialog.getInt(self, "Editar Produto", "Quantidade:", value=product["quantity"])
        if not ok: return
        product["name"] = name
        product["price"] = price
        product["quantity"] = quantity
        save_data(self.data)
        self.update_product_table()
        self.update_sales_table()

    # Excluir produto
    def delete_product(self):
        selected = self.product_table.currentRow()
        if selected == -1:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um produto")
            return
        product = self.data["products"][selected]
        reply = QtWidgets.QMessageBox.question(
            self, "Excluir Produto",
            f"Tem certeza que deseja excluir '{product['name']}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.data["products"].pop(selected)
            self.data["sales"] = [s for s in self.data["sales"] if s["product_id"] != product["id"]]
            save_data(self.data)
            self.update_product_table()
            self.update_sales_table()

    # Registrar venda
    def sell_product(self):
        selected = self.product_table.currentRow()
        if selected == -1:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um produto")
            return
        product = self.data["products"][selected]
        quantity, ok = QtWidgets.QInputDialog.getInt(self, "Venda", "Quantidade vendida:")
        if not ok: return
        if product["quantity"] < quantity:
            QtWidgets.QMessageBox.critical(self, "Erro", "Estoque insuficiente")
            return
        product["quantity"] -= quantity
        sale = Sale(product["id"], quantity, product["price"]*quantity)
        self.data["sales"].append(sale.__dict__)
        save_data(self.data)
        self.update_product_table()
        self.update_sales_table()

    # Total vendido
    def total_sales(self):
        total = sum(s["total"] for s in self.data["sales"] if self.product_exists(s["product_id"]))
        QtWidgets.QMessageBox.information(self, "Total vendido", f"Total vendido: R${total}")

    # Total vendido por período
    def total_sales_period(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Selecione Período")
        layout = QtWidgets.QVBoxLayout(dialog)

        layout.addWidget(QtWidgets.QLabel("Data inicial:"))
        start_date = QtWidgets.QDateEdit()
        start_date.setCalendarPopup(True)
        start_date.setDisplayFormat("dd/MM/yyyy")
        start_date.setDate(QtCore.QDate.currentDate().addMonths(-1))
        layout.addWidget(start_date)

        layout.addWidget(QtWidgets.QLabel("Data final:"))
        end_date = QtWidgets.QDateEdit()
        end_date.setCalendarPopup(True)
        end_date.setDisplayFormat("dd/MM/yyyy")
        end_date.setDate(QtCore.QDate.currentDate())
        layout.addWidget(end_date)

        btn_ok = QtWidgets.QPushButton("Calcular Total")
        layout.addWidget(btn_ok)

        def calculate():
            start = start_date.date().toPyDate()
            end = end_date.date().toPyDate()
            if start > end:
                QtWidgets.QMessageBox.critical(self, "Erro", "Data inicial maior que a final!")
                return
            total = sum(s["total"] for s in self.data["sales"]
                        if start <= datetime.fromisoformat(s["date"]).date() <= end
                        and self.product_exists(s["product_id"]))
            QtWidgets.QMessageBox.information(
                self,
                "Total vendido",
                f"Total vendido de {start.strftime('%d/%m/%Y')} até {end.strftime('%d/%m/%Y')}: R${total}"
            )
            dialog.close()

        btn_ok.clicked.connect(calculate)
        dialog.exec()

    def product_exists(self, product_id):
        return any(p["id"] == product_id for p in self.data["products"])

# Rodar app
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec())
