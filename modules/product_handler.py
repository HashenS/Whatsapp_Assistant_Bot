import pandas as pd
import os

class ProductHandler:
  def __init__(self, csv_path):
        self.csv_path = csv_path
        #load the database into a DataFrame

        self.df = pd.read_csv(csv_path)
      
  def get_product(self, item_id):
      #look for the product by its ID
      product = self.df[self.df['item_id'] == item_id]
      if not product.empty:
          return product.iloc[0].to_dict()
      return None
  
  def check_stock(self, item_id, qty):
      product = self.get_product(item_id)
      if product and product['stock'] >= qty:
          return True
      return False
  
  def update_stock(self, item_id, qty):
      # Reduce stock after a successful sale
        self.df.loc[self.df['item_id'] == item_id, 'stock'] -= qty
        self.df.to_csv(self.csv_path, index=False)
        print(f"✅ Stock updated for {item_id}")