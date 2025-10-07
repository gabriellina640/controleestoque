from PyQt6 import QtWidgets, QtCore
from datetime import datetime
import sys, json, os

# 📁 Pasta de dados
APP_NAME = "RTImportacoes"
if os.name == "nt":
    DATA_DIR = os.path.join(os.getenv("LOCALAPPDATA"), APP_NAME)
else:
    DATA_DIR = os.path.join(os.path.expanduser("~"), f".{APP_NAME.lower()}")
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, "database.json")

# 📝 Classes
class Product:
    def __init__(self, id, name, price, quantity):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.date_added = datetime.now().isoformat()

class Sale:
    def __init__(self, product_id, quantity_sold, total):
        self.product_id = product_id
        self.quantity_sold = quantity_sold
        self.total = total
        self.date = datetime.now().isoformat()

# 💾 Funções de persistência
def load_data():
    if not os.path.exists(DB_FILE):
        return {"products": [], "sales": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# 🖥️ App
class InventoryApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(200, 100, 950, 550)
        self.data = load_data()
        self.setup_ui()
        self.update_product_table()
        self.update_sales_table()

    def setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout()
        central.setLayout(layout)

        # Menu suspenso
        menubar = self.menuBar()
        menu = menubar.addMenu("Menu")
        menu.addAction("Total Vendido", self.total_sales)
        menu.addAction("Total por Período", self.total_sales_period)

        # Busca produtos
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Buscar produto...")
        self.search_input.textChanged.connect(self.update_product_table)
        layout.addWidget(self.search_input)

        # Tabela produtos
        self.product_table = QtWidgets.QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(["ID", "Nome", "Preço", "Quantidade", "Ações"])
        self.product_table.horizontalHeader().setStretchLastSection(True)
        self.product_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.product_table)

        # Botões
        btn_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(btn_layout)
        self.btn_add = QtWidgets.QPushButton("Adicionar Produto")
        self.btn_add.clicked.connect(self.add_product)
        btn_layout.addWidget(self.btn_add)

        self.btn_sell = QtWidgets.QPushButton("Registrar Venda")
        self.btn_sell.clicked.connect(self.sell_product)
        btn_layout.addWidget(self.btn_sell)

        # Busca vendas
        self.sales_search = QtWidgets.QLineEdit()
        self.sales_search.setPlaceholderText("Buscar venda por produto...")
        self.sales_search.textChanged.connect(self.update_sales_table)
        layout.addWidget(self.sales_search)

        # Tabela vendas
        self.sales_table = QtWidgets.QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["Produto", "Quantidade", "Total", "Data", "ID Produto"])
        self.sales_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.sales_table)

    # Atualiza produtos
    def update_product_table(self):
        search_text = self.search_input.text().lower()
        products = [p for p in self.data["products"] if search_text in p["name"].lower()]
        self.product_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.product_table.setItem(row, 0, QtWidgets.QTableWidgetItem(p["id"]))
            self.product_table.setItem(row, 1, QtWidgets.QTableWidgetItem(p["name"]))
            self.product_table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"R${p['price']}"))
            self.product_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(p["quantity"])))
            # Botões de ação
            btn_edit = QtWidgets.QPushButton("Editar")
            btn_edit.clicked.connect(lambda checked, pid=p["id"]: self.edit_product(pid))
            btn_delete = QtWidgets.QPushButton("Excluir")
            btn_delete.clicked.connect(lambda checked, pid=p["id"]: self.delete_product(pid))
            widget = QtWidgets.QWidget()
            h_layout = QtWidgets.QHBoxLayout()
            h_layout.addWidget(btn_edit)
            h_layout.addWidget(btn_delete)
            h_layout.setContentsMargins(0,0,0,0)
            widget.setLayout(h_layout)
            self.product_table.setCellWidget(row, 4, widget)

    # Atualiza vendas
    def update_sales_table(self):
        search_text = self.sales_search.text().lower()
        sales = [s for s in self.data["sales"]
                 if any(p["id"]==s["product_id"] and search_text in p["name"].lower() for p in self.data["products"])]
        self.sales_table.setRowCount(len(sales))
        for row, s in enumerate(sales):
            prod = next((p for p in self.data["products"] if p["id"]==s["product_id"]), None)
            self.sales_table.setItem(row, 0, QtWidgets.QTableWidgetItem(prod["name"] if prod else "Produto excluído"))
            self.sales_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(s["quantity_sold"])))
            self.sales_table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"R${s['total']}"))
            self.sales_table.setItem(row, 3, QtWidgets.QTableWidgetItem(s["date"]))
            self.sales_table.setItem(row, 4, QtWidgets.QTableWidgetItem(s["product_id"]))

    # Adicionar produto
    def add_product(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Produto", "Nome do produto:")
        if not ok or not name: return
        price, ok = QtWidgets.QInputDialog.getDouble(self, "Produto", "Preço:")
        if not ok: return
        quantity, ok = QtWidgets.QInputDialog.getInt(self, "Produto", "Quantidade:")
        if not ok: return
        product_id = str(len(self.data["products"]) + 1)
        self.data["products"].append(Product(product_id, name, price, quantity).__dict__)
        save_data(self.data)
        self.update_product_table()

    # Editar produto
    def edit_product(self, product_id):
        product = next(p for p in self.data["products"] if p["id"]==product_id)
        name, ok = QtWidgets.QInputDialog.getText(self, "Editar Produto", "Nome:", text=product["name"])
        if not ok: return
        price, ok = QtWidgets.QInputDialog.getDouble(self, "Editar Produto", "Preço:", value=product["price"])
        if not ok: return
        quantity, ok = QtWidgets.QInputDialog.getInt(self, "Editar Produto", "Quantidade:", value=product["quantity"])
        if not ok: return
        product["name"], product["price"], product["quantity"] = name, price, quantity
        save_data(self.data)
        self.update_product_table()
        self.update_sales_table()

    # Excluir produto
    def delete_product(self, product_id):
        self.data["products"] = [p for p in self.data["products"] if p["id"] != product_id]
        save_data(self.data)
        self.update_product_table()
        self.update_sales_table()

    # Registrar venda
    def sell_product(self):
        selected = self.product_table.currentRow()
        if selected == -1:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um produto")
            return
        product_id = self.product_table.item(selected,0).text()
        product = next(p for p in self.data["products"] if p["id"]==product_id)
        quantity, ok = QtWidgets.QInputDialog.getInt(self, "Venda", "Quantidade vendida:")
        if not ok: return
        if product["quantity"] < quantity:
            QtWidgets.QMessageBox.critical(self, "Erro", "Estoque insuficiente")
            return
        product["quantity"] -= quantity
        sale = Sale(product_id, quantity, product["price"]*quantity)
        self.data["sales"].append(sale.__dict__)
        save_data(self.data)
        self.update_product_table()
        self.update_sales_table()

    # Total vendido
    def total_sales(self):
        total = sum(s["total"] for s in self.data["sales"] if any(p["id"]==s["product_id"] for p in self.data["products"]))
        QtWidgets.QMessageBox.information(self, "Total vendido", f"Total vendido: R${total}")

    # Total por período
    def total_sales_period(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Total por período")
        layout = QtWidgets.QVBoxLayout(dialog)

        start_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        start_date.setCalendarPopup(True)
        layout.addWidget(QtWidgets.QLabel("Data inicial:"))
        layout.addWidget(start_date)

        end_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        end_date.setCalendarPopup(True)
        layout.addWidget(QtWidgets.QLabel("Data final:"))
        layout.addWidget(end_date)

        btn = QtWidgets.QPushButton("Calcular")
        layout.addWidget(btn)

        def calculate():
            start = datetime.strptime(start_date.text(), "%d/%m/%Y")
            end = datetime.strptime(end_date.text(), "%d/%m/%Y")
            total = sum(s["total"] for s in self.data["sales"]
                        if start <= datetime.fromisoformat(s["date"]) <= end)
            QtWidgets.QMessageBox.information(dialog, "Total vendido", f"Total vendido: R${total}")
        btn.clicked.connect(calculate)
        dialog.exec()

# Rodar app
app = QtWidgets.QApplication(sys.argv)
window = InventoryApp()
window.show()
sys.exit(app.exec())
