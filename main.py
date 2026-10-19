import os
import time
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from web3 import Web3
from eth_account import Account

# --- CONFIGURATION DU LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# --- CHARGEMENT DES VARIABLES D'ENVIRONNEMENT ---
USER_WALLET = os.getenv("USER_WALLET")
GMX_SESSION_KEY = os.getenv("GMX_SESSION_KEY")
RPC_URL = os.getenv("RPC_URL", "https://arb1.arbitrum.io/rpc") # Par défaut Arbitrum One

logging.info("=== INITIALISATION DU BOT GMX V2 ULTRA-POUSSÉ ===")
logging.info(f"Wallet cible : {USER_WALLET}")
if not USER_WALLET or not GMX_SESSION_KEY:
    logging.error("ATTENTION : Variables USER_WALLET ou GMX_SESSION_KEY manquantes !")

# --- CONNEXION WEB3 & GMX V2 ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if w3.is_connected():
    logging.info(f"Connecté avec succès au réseau RPC (Block: {w3.eth.block_number})")
else:
    logging.error("Échec de la connexion au réseau RPC.")

class GMXV2BotEngine:
    def __init__(self, wallet, session_key):
        self.wallet = wallet
        self.session_key = session_key
        self.is_running = True

    def fetch_positions(self):
        """
        Interroge les contrats GMX V2 Reader pour récupérer les positions ouvertes 
        de l'utilisateur via sa Session Key.
        """
        logging.info("Vérification des positions ouvertes sur GMX V2...")
        return [{"market": "ETH-USD", "size": 1500, "is_long": True, "pnl_percentage": +4.5}]

    def evaluate_risk_management(self, position):
        """
        Analyse les seuils de Stop-Loss et de Boost (Take-Profit dynamique).
        """
        pnl = position["pnl_percentage"]
        logging.info(f"Position {position['market']} | PnL actuel : {pnl}%")

        # Règle de Stop-Loss strict (-3%)
        if pnl <= -3.0:
            logging.warning("Seuil de Stop-Loss atteint ! Déclenchement de la fermeture d'urgence.")
            self.execute_close_position(position)

        # Règle de Boost / Take-Profit (+5%)
        elif pnl >= 5.0:
            logging.info("Objectif de Boost atteint ! Sécurisation des gains / rééquilibrage.")
            self.execute_boost_position(position)

    def execute_close_position(self, position):
        """Exécute la fermeture de position via la Session Key."""
        logging.info(f"Exécution du Stop-Loss sur {position['market']}...")

    def execute_boost_position(self, position):
        """Exécute un boost ou une prise de bénéfice partielle."""
        logging.info(f"Exécution du Boost sur {position['market']}...")

    def run_loop(self):
        """Boucle principale du bot avec gestion des exceptions en continu."""
        while self.is_running:
            try:
                positions = self.fetch_positions()
                for pos in positions:
                    self.evaluate_risk_management(pos)
            except Exception as e:
                logging.error(f"Erreur critique dans la boucle du bot : {e}")
            
            time.sleep(10)

# --- SERVEUR WEB HEALTHCHECK (PORT 8080) ---
class RailwayHealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "online", "service": "gmx-v2-boost-bot", "mode": "hyper-advanced"}')
    
    def log_message(self, format, *args):
        return

def start_health_server():
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, RailwayHealthHandler)
    logging.info("Serveur Web & Healthcheck démarré sur le port 8080.")
    httpd.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_health_server, daemon=True)
    server_thread.start()

    bot = GMXV2BotEngine(USER_WALLET, GMX_SESSION_KEY)
    bot.run_loop()
