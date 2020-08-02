from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os
from datetime import datetime as dt
import statsapi
import textwrap

"""
MLB Scoring Plays Bot process.
"""

# flask
app = Flask(__name__)

# consts
TEAM_MAP = {
    "AZ": "Arizona Diamondbacks",
    "ATL": "Atlanta Braves",
    "BAL": "Baltimore Orioles",
    "BOS": "Boston Red Sox",
    "CHC": "Chicago Cubs",
    "CWS": "Chicago White Sox",
    "CIN": "Cincinnati Reds",
    "COL": "Colorado Rockies",
    "CLE": "Cleveland Indians",
    "DET": "Detroit Tigers",
    "HOU": "Houston Astros",
    "KC": "Kansas City Royals",
    "LAA": "Los Angeles Angels",
    "LAD": "Los Angeles Dodgers",
    "MIA": "Miami Marlins",
    "MIL": "Milwaukee Brewers",
    "MIN": "Minnesota Twins",
    "NYM": "New York Mets",
    "NYY": "New York Yankees",
    "OAK": "Oakland Athletics",
    "PHI": "Philadelphia Phillies",
    "PIT": "Pittsburgh Pirates",
    "SD": "San Diego Padres",
    "SF": "San Francisco Giants",
    "SEA": "Seattle Mariners",
    "STL": "St. Louis Cardinals",
    "TB": "Tampa Bay Rays",
    "TEX": "Texas Rangers",
    "TOR": "Toronto Blue Jays",
    "WSH": "Washington Nationals"
}

# auth info
BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_SECRET = os.environ["BOT_SECRET"]

# bot application
bot = LineBotApi(BOT_TOKEN)
handler = WebhookHandler(BOT_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return f"process successed!: {body}"
    
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    send_messages = []

    abr_team_nm = event.message.text.upper()
    team_nm = TEAM_MAP[abr_team_nm]
    games = statsapi.schedule()
    for game in games:
        home = game["home_name"]
        away = game["away_name"]
        if home == team_nm or away == team_nm:
            status = game["status"]
            home_score = game["home_score"]
            away_score = game["away_score"]
            summary = f"[{status}]\n{home} {home_score} - {away_score} {away}"
            send_messages.append(TextSendMessage(text=summary))
            game_id = game["game_id"]
            scoring_plays = statsapi.game_scoring_plays(game_id)
            if scoring_plays != "":
                send_messages.append(TextSendMessage(text=scoring_plays))
    if len(send_messages) != 0:
        bot.reply_message(
            event.reply_token, send_messages
        )
    else:
        error_message = TextSendMessage(text=f"{abr_team_nm}の試合が見つかりませんでした。")
        bot.reply_message(
            event.reply_token, error_message
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)