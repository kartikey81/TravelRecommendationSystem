#from dotenv import load_dotenv
import os
import openai
#import googlemaps
from flask import Flask, request, render_template

# Set up OpenAI API client

openai.api_key = os.environ.get('OPENAI_API_KEY')
model_engine = "text-davinci-003"

# Set up Google Maps client
#gmaps = googlemaps.Client(key=os.environ.get('google_maps_key'))


# Set up Flask app
app = Flask(__name__, static_url_path='/static')

# Populate prompt function
def populate_prompt(user_input_start_location: str, user_input_description: str) -> str:
    return f"You are powering a travel recommendations app which prioritises diversified recommendations of places people should visit. \
            List 5 destinations to travel to from {user_input_start_location} that match the description: {user_input_description}. \
            Provide the country they are in and a short description of each one explaining why it fits the required description, along with some sights to visit in the location. \
            The descriptions you provide should not repeat any phrases or sentence structures, and should not start with the destination name. \
            Your response should be in python dict format where the key is each destination name, and value is the description. \
            Here is the expected format: \
                {{ \
                    0: {{\"name\": \"destination first name 1\", \"country\": \"country of destination 1\", \"description\": \"description of destination 1\"}}, \
                    \
                    4: {{\"name\": \"destination first name 5\", \"country\": \"country of destination 5\", \"description\": \"description of destination 5\"}}, \
                }} \
            Any apostrophes should have a backlash in front of them."

# Call api function
def call_openai_api(prompt: str) -> str:
   return openai.Completion.create(
            model=model_engine,
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.5,
        )

'''def get_locations_for_map(prompt_dict):
    locations = []
    for i in range(len(prompt_dict)):
        location_full_name = f"{prompt_dict[i]['name']}, {prompt_dict[i]['country']}"
        geocode_result = gmaps.geocode(location_full_name)
        lat = geocode_result[0]["geometry"]["location"]["lat"]
        lng = geocode_result[0]["geometry"]["location"]["lng"]
        locations.append({"name": location_full_name, "lat": lat, "lng": lng})
    return locations
'''
# Define route for home page
@app.route("/", methods=["GET", "POST"])
def home():
    #locations = []
    prompt_html = None
    user_input_start_location = ""
    user_input_description = ""
    if request.method == "POST":
        # Get text from input field
        user_input_start_location = request.form["start_loc"]
        user_input_description = request.form["loc_description"]

        # Create prompt
        prompt = populate_prompt(user_input_start_location, user_input_description)

        # Make API request to OpenAI to generate completion
        response = call_openai_api(prompt)

        # Extract response text from API response
        prompt_dict = eval(response.choices[0].text)

        # Render home page with formatted bullet point list
        prompt_html = [
            f"{prompt_dict[i]['name']}, {prompt_dict[i]['country']} - {prompt_dict[i]['description']}" for i in range(len(prompt_dict))]

        
        # Get latitude and longitude for each location
        #locations = get_locations_for_map(prompt_dict)

    # Render home page with input field and submit button
    return render_template("index.html",
                           prompt_html=prompt_html,
                           
                           user_input_start_location=user_input_start_location,
                           user_input_description=user_input_description)


# Run app
if __name__ == "__main__":
    app.run(debug=True)
