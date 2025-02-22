from flask import Flask, request, jsonify
from seleniumbase import SB
import logging
import os
import psutil
import time
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Initial configuration
resource_timeout = int(os.getenv("RESOURCE_TIMEOUT", 60))
concurrent_seleniumbase = 0
lock = threading.Lock()

def fetch_html(url, proxy=None):
    """Fetch HTML content using SeleniumBase."""
    global concurrent_seleniumbase
    with lock:
        concurrent_seleniumbase += 1
    try:
        with SB(uc=True, headless=True, locale_code="en", data="./data", proxy=proxy) as sb:
            sb.activate_cdp_mode(url)

            if sb.is_element_present("#iframe_title"):
                html = sb.get_page_source()
                logging.info("No Captcha!")
                return {"html": html, "captchaDetected": False}  # Changed key here
            else:
                if not sb.is_element_present(".cf-turnstile"):
                    html = sb.get_page_source()
                    logging.info("No Captcha!")
                    html = sb.get_page_source()
                    return {"html": html, "captchaDetected": False}  # Changed key here
                else:
                    logging.info("Captcha Detected!")
                    sb.wait_for_element("#iframe_title", "css selector", 20)
                    html = sb.get_page_source()
                    logging.info("Captcha Solved (confirmed)!")
                    return {"html": html, "captchaDetected": True}  # Changed key here
    finally:
        with lock:
            concurrent_seleniumbase -= 1

def can_process_request():
    """Check if there are enough resources to process a new request."""
    # if concurrent_seleniumbase == 0:
    #     return True
    cpu_usage = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    free_memory = memory_info.available / (1024 * 1024)  # Convert to MB

    # Calculate if we can process a new request
    return free_memory > 300 and cpu_usage < 80  # Example thresholds

def wait_for_resources(timeout=resource_timeout):
    """Wait until resources are available to process a request, with a timeout."""
    start_time = time.time()
    while not can_process_request():
        if time.time() - start_time > timeout:
            logging.warning("Timeout waiting for resources.")
            return False
        logging.info("Waiting for resources to become available...")
        time.sleep(1)  # Wait before checking again
    return True

@app.route('/fetch', methods=['GET', 'POST'])
def fetch():
    """API endpoint to fetch HTML content."""
    start_time = time.time()  # Start timing

    if request.method == 'GET':
        url = request.args.get('url')
        proxy = request.args.get('proxy', None)
    elif request.method == 'POST':
        data = request.get_json()
        url = data.get('url')
        proxy = data.get('proxy', None)
    else:
        return jsonify({"error": "Invalid request method."}), 405

    if not url:
        return jsonify({"error": "URL parameter is required."}), 400

    logging.info(f"Received request to fetch URL: {url} with proxy: {proxy}")

    # Wait for resources to become available
    if not wait_for_resources(timeout=resource_timeout):
        return jsonify({"error": "Timeout waiting for resources."}), 503

    # Process the request
    logging.info("Processing request...")
    try:
        result = fetch_html(url, proxy)
    except Exception as e:
        logging.error(f"Error fetching HTML: {e}")
        return jsonify({"error": str(e)}), 500

    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    result['time'] = elapsed_time  # Keep the key as 'time'

    return jsonify(result), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, threaded=True)
