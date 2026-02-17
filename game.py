import pygame
import sys
import time
import json
from web3 import Web3
from eth_account import Account

# --- Blockchain Config ---
INFURA_URL = 'https://sepolia.infura.io/v3/YOUR_KEY'
PRIVATE_KEY = 'YOUR_PRIVATE_KEY'
MY_WALLET = '0xYourAddress'

# --- Monetization Config ---
TAX_PERCENT = 10  # 10% Fee for the Developer

# --- Colors ---
BG_COLOR = (20, 24, 30)
CARD_COLOR = (30, 36, 46)
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (0, 210, 211)
BUTTON_COLOR = (44, 52, 66)
BUTTON_HOVER = (60, 70, 88)
SUCCESS_COLOR = (80, 200, 120)
SHOP_COLOR = (255, 165, 0)
BLACK = (0, 0, 0)
RED = (220, 80, 80)

# --- Save System ---
def save_game(score, cp, am, cpc, amc):
    data = {"score": score, "click_power": cp, "auto_mine": am, "click_power_cost": cpc, "auto_mine_cost": amc}
    with open("save_data.json", "w") as f:
        json.dump(data, f)

def load_game():
    try:
        with open("save_data.json", "r") as f:
            return json.load(f)
    except: return None

def send_crypto(amount_in_ether):
    try:
        w3 = Web3(Web3.HTTPProvider(INFURA_URL))
        if not w3.is_connected(): return "No Connection"
        account = Account.from_key(PRIVATE_KEY)
        nonce = w3.eth.get_transaction_count(account.address)
        tx = {'nonce': nonce, 'to': MY_WALLET, 'value': w3.to_wei(amount_in_ether, 'ether'), 'gas': 21000, 'gasPrice': w3.to_wei('10', 'gwei'), 'chainId': 11155111}
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return "Sent!"
    except: return "Error"

def draw_rounded_rect(surface, color, rect, rad=15):
    pygame.draw.rect(surface, color, rect, border_radius=rad)

def draw_small_btn(surface, text, cost, x, y, w, h, action):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    color = BUTTON_HOVER if (x < mouse[0] < x + w and y < mouse[1] < y + h) else BUTTON_COLOR
    draw_rounded_rect(surface, color, (x, y, w, h))
    pygame.draw.rect(surface, SHOP_COLOR, (x, y, w, h), 2, border_radius=15)
    surface.blit(font_small.render(text, True, TEXT_COLOR), (x + 10, y + 10))
    surface.blit(font_small.render(f"{cost} Coins", True, SHOP_COLOR), (x + 10, y + 35))
    if click[0] == 1 and action and (x < mouse[0] < x + w and y < mouse[1] < y + h):
        action()
        pygame.time.delay(150)

# --- Setup ---
pygame.init()
screen = pygame.display.set_mode((400, 750)) # Increased height for new info
clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)
font_large = pygame.font.Font(None, 80)
font_small = pygame.font.Font(None, 24)
font_tiny = pygame.font.Font(None, 20)

# --- Load Data ---
data = load_game()
score = data["score"] if data else 0
click_power = data["click_power"] if data else 1
auto_mine = data["auto_mine"] if data else 0
click_power_cost = data["click_power_cost"] if data else 10
auto_mine_cost = data["auto_mine_cost"] if data else 50
status_msg = "Game Loaded" if data else "New Game"

click_effects = []
floating_texts = []
last_auto_time = time.time()

# --- Actions ---
def mine_action():
    global score
    score += click_power
    mx, my = pygame.mouse.get_pos()
    click_effects.append({'x': mx, 'y': my, 'r': 5, 'alpha': 255})
    floating_texts.append({'text': f"+{click_power}", 'x': mx, 'y': my, 'life': 60})

def buy_click_upgrade():
    global score, click_power, click_power_cost
    if score >= click_power_cost:
        score -= click_power_cost
        click_power += 1
        click_power_cost = int(click_power_cost * 1.5)
        save_game(score, click_power, auto_mine, click_power_cost, auto_mine_cost)

def buy_auto_upgrade():
    global score, auto_mine, auto_mine_cost
    if score >= auto_mine_cost:
        score -= auto_mine_cost
        auto_mine += 1
        auto_mine_cost = int(auto_mine_cost * 1.6)
        save_game(score, click_power, auto_mine, click_power_cost, auto_mine_cost)

def withdraw_action():
    global score, status_msg
    # Calculate Fee
    fee = score * (TAX_PERCENT / 100)
    net_amount = score - fee
    
    # Minimum withdraw check (e.g., 50)
    if net_amount >= 50:
        status_msg = f"Sending {net_amount:.1f} (Fee: {fee:.1f})"
        # Convert to Ether logic (assuming 1 Coin = 0.00001 Ether for example)
        eth_amount = net_amount * 0.00001 
        res = send_crypto(eth_amount)
        if "Sent" in res:
            score = 0
            status_msg = "Withdraw Successful!"
            save_game(score, click_power, auto_mine, click_power_cost, auto_mine_cost)
        else:
            status_msg = "Tx Failed"
    else:
        status_msg = f"Min 50 Coins (Net)"

# --- Main Loop ---
running = True
while running:
    screen.fill(BG_COLOR)
    
    if time.time() - last_auto_time >= 1:
        score += auto_mine
        last_auto_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game(score, click_power, auto_mine, click_power_cost, auto_mine_cost)
            running = False

    # UI
    draw_rounded_rect(screen, CARD_COLOR, (20, 20, 360, 120), rad=15)
    pygame.draw.circle(screen, ACCENT_COLOR, (200, 60), 25, 3)
    screen.blit(font.render("$", True, ACCENT_COLOR), (192, 47))
    screen.blit(font_large.render(str(int(score)), True, TEXT_COLOR), (140, 50))
    screen.blit(font_small.render(f"Power: {click_power} | Auto: {auto_mine}/s", True, (150,150,150)), (80, 100))

    mx, my = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if click[0] == 1 and 50 < mx < 350 and 160 < my < 360:
        mine_action()

    pygame.draw.circle(screen, BUTTON_COLOR, (200, 260), 90)
    pygame.draw.circle(screen, ACCENT_COLOR, (200, 260), 90, 4)
    screen.blit(font.render("TAP", True, ACCENT_COLOR), (155, 250))

    screen.blit(font.render("UPGRADES", True, TEXT_COLOR), (20, 390))
    draw_small_btn(screen, "Click +1", click_power_cost, 20, 430, 360, 60, buy_click_upgrade)
    draw_small_btn(screen, "Auto +1", auto_mine_cost, 20, 510, 360, 60, buy_auto_upgrade)

    # Fee Info
    fee_text = font_tiny.render(f"Withdraw Fee: {TAX_PERCENT}%", True, RED)
    screen.blit(fee_text, (20, 590))

    screen.blit(font_tiny.render(status_msg, True, (150,150,150)), (20, 610))
    
    # Withdraw Button
    draw_rounded_rect(screen, SUCCESS_COLOR, (20, 640, 360, 60), rad=10)
    screen.blit(font.render("WITHDRAW ALL", True, BLACK), (95, 655))
    if click[0] == 1 and 20 < mx < 380 and 640 < my < 700:
        withdraw_action()

    # Effects
    for effect in click_effects[:]:
        effect['r'] += 2; effect['alpha'] -= 8
        if effect['alpha'] <= 0: click_effects.remove(effect)
        else:
            s = pygame.Surface((effect['r']*2, effect['r']*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*ACCENT_COLOR, effect['alpha']), (effect['r'], effect['r']), effect['r'], 2)
            screen.blit(s, (effect['x'] - effect['r'], effect['y'] - effect['r']))

    for txt in floating_texts[:]:
        txt['y'] -= 1; txt['life'] -= 1
        if txt['life'] <= 0: floating_texts.remove(txt)
        else:
            alpha = int((txt['life'] / 60) * 255)
            ts = font.render(txt['text'], True, ACCENT_COLOR)
            ts.set_alpha(alpha)
            screen.blit(ts, (txt['x'], txt['y']))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()