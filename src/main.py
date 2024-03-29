from config import *

__app__ = Flask(__name__, template_folder=abspath('web/'), static_folder=abspath('web/static'))

# authentication

fetilizer_model = load(fertilizer_model_dir)
fertilizer_rqcolumns = ['Temperature', 'Humidity', 'Moisture', 'Soil Type', 'Crop Type', 'Nitrogen', 'Potassium', 'Phosphorous']

disease_model = {
    "apple" : load_model(d_model_apple_dir),
    "potato" : load_model(d_model_potato_dir),
    "tomato": load_model(d_model_tomato_dir),
    "rice": load_model(d_model_rice_dir),
    "corn": load_model(d_model_corn_dir)
}

disease_label = {
    "apple": ["brown_spot", "healthy", "mosaic"],
    "potato": ["fungi",  "healthy", "nematode"],
    "rice": ['leaf blight', 'brown spot', 'healthy', "leaf blast", "leaf scald", 'narrow brown spot'],
    "corn": ["blight", "common rust", "healthy"],
    "tomato": ["healthy", "late blight", "septoria leaf spot", "yellow leaf curl"]
}

market_models = {}
for filename in listdir(market_dir):
    if filename.endswith('.pkl'):
        commodity = filename.split('_')[0]
        model_path = join(market_dir, filename)
        try:
            model = load(model_path)
            market_models[commodity] = model
        except Exception as e:
            print(f"Error loading model '{filename}': {str(e)}")

# home

@__app__.route('/')
def home():
    return render_template("index.html")

@__app__.route('/fertilizer')
def fertilizer():
    return render_template("fertilizer.html")

@__app__.route('/fertilizer', methods=['POST'])
def process_fertilizer_form():
    try:
        temperature = request.form.get('temperature')
        humidity = request.form.get('humidity')
        moisture = request.form.get('moisture')
        soil_type = request.form.get('soil_type')
        crop_type = request.form.get('crop_type')
        nitrogen = request.form.get('nitrogen')
        potassium = request.form.get('potassium')
        phosphorous = request.form.get('phosphorous')

        input_data = pd.DataFrame([[temperature, humidity, moisture, soil_type, crop_type, nitrogen, potassium, phosphorous]],
                                columns=fertilizer_rqcolumns)

        prediction = fetilizer_model.predict(input_data)

        return jsonify({"prediction": prediction[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@__app__.route('/disease')
def disease():
    return render_template("disease.html")

@__app__.route('/disease', methods=['POST'])
def process_disease_form():
    leaf_type = request.form.get('dropdown')
    file = request.files['image']
    try:
        image = Image.open(file)
        img_array = img_to_array(image.resize((224,224)))
        
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        predictions = (disease_model[leaf_type]).predict(img_array)
        predicted_label = np.argmax(predictions, axis=1)

        prediction = (disease_label[leaf_type])[predicted_label[0]]
        
        return jsonify({"prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@__app__.route('/market')
def market():
    return render_template("market.html")

@__app__.route('/market', methods=['POST'])
def process_market_form():
    commodity = request.form.get('commodity')
    date = request.form.get('date')

    print(f"{commodity} for {date}")
    try:
        date_ordinal = pd.to_datetime(date).toordinal()
        print(market_models[commodity])
        prediction = (market_models[commodity]).predict([[date_ordinal]])

        return jsonify({"prediction": float(prediction)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# docs

@__app__.route('/docs')
def docs():
    return render_template("docs/index.html")

# api

@__app__.route('/api/fertilizer', methods=['GET'])
def api_fertilizer():
    try:
        temperature = float(request.args.get('temperature'))
        humidity = float(request.args.get('humidity'))
        moisture = float(request.args.get('moisture'))
        soil_type = request.args.get('soil_type')
        crop_type = request.args.get('crop_type')
        nitrogen = float(request.args.get('nitrogen'))
        potassium = float(request.args.get('potassium'))
        phosphorous = float(request.args.get('phosphorous'))

        input_data = pd.DataFrame([[temperature, humidity, moisture, soil_type, crop_type, nitrogen, potassium, phosphorous]],
                                  columns=['Temperature', 'Humidity', 'Moisture', 'Soil Type', 'Crop Type', 'Nitrogen', 'Potassium', 'Phosphorous'])

        prediction = fetilizer_model.predict(input_data)

        return jsonify({"prediction": prediction[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@__app__.route('/api/disease/<leaf_type>', methods=['GET'])
def api_disease(leaf_type):
    try:
        file = request.args.get('file')
        url = request.args.get('url').strip('"')

        if file:
            image = Image.open(BytesIO(file.read()))
        elif url:
            response = requests.get(url)
            if response.status_code != 200:
                return jsonify({"error": "Invalid URL or unable to fetch image"})
            image = Image.open(BytesIO(response.content))
        else:
            return jsonify({"error": "No file or URL provided"})

        img_array = img_to_array(image.resize((224,2)))
        
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        predictions = disease_model[leaf_type].predict(img_array)
        predicted_label = np.argmax(predictions, axis=1)

        prediction = (disease_label[leaf_type])[predicted_label[0]]

        return jsonify({"prediction": prediction})

    except Exception as e:
        return jsonify({"error": str(e)}), 400
        

@__app__.route('/api/market', methods=['GET'])
def api_market():
    commodity = request.args.get('commodity')

    if commodity in market_models:
        try:
            date = request.args.get('date')
            date_ordinal = pd.to_datetime(date).toordinal()
        
            prediction = (market_models[commodity]).predict([[date_ordinal]])

            return jsonify({"prediction": float(prediction)})
        except Exception as e:
            return jsonify({"error": str(e)}), 400


@__app__.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

if __name__ == '__main__':
    __app__.run(debug=True, port=8888)