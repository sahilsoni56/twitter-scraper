from flask import Flask, render_template, jsonify
from scraper import TwitterScraper
import json

app = Flask(__name__, template_folder='../templates')
scraper = TwitterScraper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape')
def scrape():
    try:
        result = scraper.get_trending_topics()
        trends = []
        
        for i in range(1, 6):
            if result.get(f'nameoftrend{i}'):
                trends.append({
                    'name': result[f'nameoftrend{i}'],
                    'category': result[f'trend_category{i}'],
                })
        
        return jsonify({
            'success': True,
            'data': {
                'trends': trends,
                'datetime': result['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                'ip_address': result['ip_address'],
                'mongodb_record': json.dumps(result, default=str)
            }
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)