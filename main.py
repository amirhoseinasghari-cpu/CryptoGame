import json
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.core.window import Window

# Blockchain imports
try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    print("Web3 not installed")

# --- Config ---
INFURA_URL = 'https://sepolia.infura.io/v3/YOUR_KEY'
PRIVATE_KEY = 'YOUR_PRIVATE_KEY'
MY_WALLET = '0xYourAddress'
TAX_PERCENT = 10

class CryptoGame(BoxLayout):
    score = NumericProperty(0)
    click_power = NumericProperty(1)
    auto_mine = NumericProperty(0)
    click_cost = NumericProperty(10)
    auto_cost = NumericProperty(50)
    status = StringProperty("Welcome")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        Window.clearcolor = (0.08, 0.09, 0.12, 1) # Dark Background
        
        self.load_data()
        # Start Auto Miner (Every 1 second)
        Clock.schedule_interval(self.auto_mine_loop, 1)

    # --- Logic ---
    def mine(self):
        self.score += self.click_power
        self.status = "Mining..."

    def auto_mine_loop(self, dt):
        if self.auto_mine > 0:
            self.score += self.auto_mine

    def buy_click(self):
        if self.score >= self.click_cost:
            self.score -= self.click_cost
            self.click_power += 1
            self.click_cost = int(self.click_cost * 1.5)
            self.status = "Upgraded Power"
            self.save_data()

    def buy_auto(self):
        if self.score >= self.auto_cost:
            self.score -= self.auto_cost
            self.auto_mine += 1
            self.auto_cost = int(self.auto_cost * 1.6)
            self.status = "Upgraded Auto"
            self.save_data()

    def withdraw(self):
        fee = self.score * (TAX_PERCENT / 100)
        net = self.score - fee
        
        if net >= 50:
            self.status = "Processing Tx..."
            # Simulating Blockchain Call
            if WEB3_AVAILABLE:
                try:
                    w3 = Web3(Web3.HTTPProvider(INFURA_URL))
                    # Add real tx logic here if needed
                    self.status = f"Sent {net:.0f} (Fee: {fee:.0f})"
                except:
                    self.status = "Connection Error"
            else:
                self.status = "Mock Tx Sent"
            
            self.score = 0
            self.save_data()
        else:
            self.status = "Min 50 Coins Net"

    # --- Save System ---
    def save_data(self):
        data = {
            "score": self.score, "cp": self.click_power,
            "am": self.auto_mine, "cpc": self.click_cost, "amc": self.auto_cost
        }
        with open("kivy_save.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        try:
            with open("kivy_save.json", "r") as f:
                d = json.load(f)
                self.score = d["score"]
                self.click_power = d["cp"]
                self.auto_mine = d["am"]
                self.click_cost = d["cpc"]
                self.auto_cost = d["amc"]
        except:
            pass

class CryptoApp(App):
    def build(self):
        # KV Language for UI Design
        self.root = CryptoGame()
        
        # Layout Structure
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        # 1. Header
        header = Label(text="Crypto Tycoon", font_size=30, size_hint_y=0.1)
        self.root.add_widget(header)
        
        # 2. Score Label (Bound to property)
        score_lbl = Label(text=f"{self.root.score}", font_size=60, size_hint_y=0.2)
        self.root.bind(score=lambda instance, value: setattr(score_lbl, 'text', str(int(value))))
        self.root.add_widget(score_lbl)
        
        # 3. Mine Button
        mine_btn = Button(text="TAP TO MINE", font_size=30, background_color=(0, 0.8, 0.8, 1), size_hint_y=0.25)
        mine_btn.bind(on_press=self.root.mine)
        self.root.add_widget(mine_btn)
        
        # 4. Upgrades Box
        upgrade_box = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
        
        btn_click = Button(text=f"Power ({self.root.click_cost})", font_size=18)
        btn_click.bind(on_press=self.root.buy_click)
        
        btn_auto = Button(text=f"Auto ({self.root.auto_cost})", font_size=18)
        btn_auto.bind(on_press=self.root.buy_auto)
        
        # Update button texts dynamically
        def update_btns(instance, value):
            btn_click.text = f"Power ({self.root.click_cost})"
            btn_auto.text = f"Auto ({self.root.auto_cost})"
            
        self.root.bind(click_cost=update_btns, auto_cost=update_btns)
        
        upgrade_box.add_widget(btn_click)
        upgrade_box.add_widget(btn_auto)
        self.root.add_widget(upgrade_box)
        
        # 5. Status
        status_lbl = Label(text="Ready", font_size=18, color=(1,0.5,0.5,1), size_hint_y=0.1)
        self.root.bind(status=lambda instance, value: setattr(status_lbl, 'text', value))
        self.root.add_widget(status_lbl)
        
        # 6. Withdraw
        with_btn = Button(text="WITHDRAW ALL", font_size=25, background_color=(0.2, 0.8, 0.2, 1), size_hint_y=0.15)
        with_btn.bind(on_press=self.root.withdraw)
        self.root.add_widget(with_btn)
        
        return self.root

if __name__ == '__main__':
    CryptoApp().run()