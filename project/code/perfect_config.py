from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    user= "root"
    password= ""
    host= "localhost"
    port= 3306
    database= "ww26_predictor"
    raw_csv_paths= {
        "fifa_ranking": "data/fifa_ranking.csv",
        "group_schedule": "data/groups_schedule.csv",
        "results": "data/results.csv",
        "squad_stats": "data/squad_stats.csv",
        "tournament_groups": "data/tournament_groups.csv",
    }


@dataclass
class PipelineConfig:
    random_state= 8
    n_splits= 5
    verbose= True
    euro_to_usd= 1.1
    max_rest_day= 14
    home_advantage= 100
    simulation_num= 1000
    home_advantage= 100
    k_friendly= 20
    k_quarter= 40
    k_tournament= 60
    k_worldcup= 70
    gd_cap= 7
    euro_to_usd= 1.1
    model_path= "saved_models/trained_models.pkl"
    match_type_order= None
    simulation_output_dir= "data/"
    features_csv= "data/match_full_features.csv"
    groups_path_csv= "data/tournament_groups.csv"
    training_table= "match_full_view"
    simulation_csv= "data/monte_carlo_predictions.csv"
    qualifier_keyword= ["qualification", "qualifier", "qualifying"]
    worldcup_keyword= ["fifa world cup"]
    tournament_keyword= [
        "african cup of nations", "uefa euro", "copa américa", "copa america",
        "gold cup", "confederations cup", "aff championship", "oceania nations cup",
        "afc asian cup", "concacaf nations league", "uefa nations league",
    ]
    valid_fifa_names= {
        "Argentina", "Spain", "France", "England", "Brazil", "Netherlands",
        "Portugal", "Belgium", "Italy", "Germany", "Croatia", "Morocco",
        "Uruguay", "Colombia", "Japan", "USA", "Mexico", "IR Iran",
        "Senegal", "Switzerland", "Denmark", "Austria", "Korea Republic",
        "Ecuador", "Ukraine", "Australia", "Türkiye", "Sweden", "Wales",
        "Canada", "Serbia", "Egypt", "Panama", "Poland", "Russia",
        "Algeria", "Hungary", "Norway", "Czechia", "Greece",
        "Côte d'Ivoire", "Peru", "Nigeria", "Scotland", "Romania",
        "Slovakia", "Venezuela", "Paraguay", "Tunisia", "Cameroon",
        "Slovenia", "Chile", "Mali", "Costa Rica", "Qatar", "South Africa",
        "Uzbekistan", "Saudi Arabia", "Iraq", "Republic of Ireland",
        "Congo DR", "Jordan", "Jamaica", "Burkina Faso",
        "United Arab Emirates", "Albania", "North Macedonia", "Georgia",
        "Finland", "Bosnia and Herzegovina", "Northern Ireland",
        "Cabo Verde", "Montenegro", "Iceland", "Honduras", "Ghana", "Oman",
        "Israel", "Gabon", "Bolivia", "El Salvador", "Guinea", "Haiti",
        "Bahrain", "Bulgaria", "New Zealand", "Angola", "Zambia", "Uganda",
        "Curaçao", "Luxembourg", "Equatorial Guinea", "Syria", "China PR",
        "Benin", "Mozambique", "Kosovo", "Belarus", "Thailand",
        "Trinidad and Tobago", "Palestine", "Armenia", "Kyrgyz Republic",
        "Tajikistan", "Comoros", "Guatemala", "Tanzania", "Namibia",
        "Vietnam", "Mauritania", "Kenya", "Lebanon", "Kazakhstan", "Sudan",
        "Madagascar", "Zimbabwe", "Libya", "Korea DPR", "Azerbaijan",
        "Togo", "Estonia", "Niger", "Indonesia", "Sierra Leone", "Congo",
        "The Gambia", "India", "Guinea-Bissau", "Cyprus", "Rwanda",
        "Malaysia", "Malawi", "Nicaragua", "Kuwait",
        "Central African Republic", "Botswana", "Suriname", "Latvia",
        "Dominican Republic", "Burundi", "Faroe Islands", "Turkmenistan",
        "Lithuania", "Liberia", "St Kitts and Nevis", "Philippines",
        "Ethiopia", "Lesotho", "Solomon Islands", "Fiji", "New Caledonia",
        "Guyana", "Hong Kong, China", "Moldova", "Eswatini", "Tahiti",
        "Puerto Rico", "Yemen", "Antigua and Barbuda", "Afghanistan",
        "Singapore", "Myanmar", "Vanuatu", "Maldives", "St Lucia",
        "Chinese Taipei", "Cuba", "Bermuda", "Malta", "South Sudan",
        "Papua New Guinea", "St Vincent and the Grenadines", "Andorra",
        "Grenada", "Nepal", "Barbados", "Chad", "Mauritius", "Belize",
        "Montserrat", "Cambodia", "Bhutan", "Bangladesh", "Dominica",
        "Brunei Darussalam", "American Samoa", "Mongolia", "Cook Islands",
        "Samoa", "Laos", "Cayman Islands", "Djibouti", "Macau",
        "São Tomé and Príncipe", "Aruba", "Gibraltar", "Timor-Leste",
        "Pakistan", "Tonga", "Sri Lanka", "Somalia", "Guam", "Seychelles",
        "Bahamas", "Liechtenstein", "Turks and Caicos Islands",
        "British Virgin Islands", "US Virgin Islands", "Anguilla", "San Marino",
    }
    renames= {
        "United States": "USA",
        "Turkey": "Türkiye",
        "Iran": "IR Iran",
        "South Korea": "Korea Republic",
        "North Korea": "Korea DPR",
        "DR Congo": "Congo DR",
        "Ivory Coast": "Côte d'Ivoire",
        "Czech Republic": "Czechia",
        "Kyrgyzstan": "Kyrgyz Republic",
        "Cape Verde": "Cabo Verde",
        "Gambia": "The Gambia",
        "Hong Kong": "Hong Kong, China",
        "Taiwan": "Chinese Taipei",
        "Brunei": "Brunei Darussalam",
        "Saint Kitts and Nevis": "St Kitts and Nevis",
        "Saint Lucia": "St Lucia",
        "Saint Vincent and the Grenadines": "St Vincent and the Grenadines",
        "United States Virgin Islands": "US Virgin Islands",
        "Vietnam Republic": "Vietnam",
        "North Vietnam": "Vietnam",
        "FYR Macedonia": "North Macedonia",
        "St. Kitts and Nevis": "St Kitts and Nevis",
        "St. Vincent and the Grenadines": "St Vincent and the Grenadines",
        "St. Lucia": "St Lucia",
        "Curacao": "Curaçao",
        "Sao Tome e Principe": "São Tomé and Príncipe",
        "Aotearoa New Zealand": "New Zealand",
        "Swaziland": "Eswatini",
        "Cape Verde Islands": "Cabo Verde",
        "St. Vincent / Grenadines": "St Vincent and the Grenadines",
        "Yugoslavia": "Serbia",
        "Serbia and Montenegro": "Serbia",
        "Zaire": "Congo DR",
        "Netherlands Antilles": "Curaçao", 
        "A. Samoa": "American Samoa",
        "Antigua and B.": "Antigua and Barbuda",
        "B. Virgin": "British Virgin Islands",
        "Bosnia": "Bosnia and Herzegovina",
        "Central Africa": "Central African Republic",
        "China": "China PR",
        "Dominican Rep.": "Dominican Republic",
        "Equat. Guinea": "Equatorial Guinea",
        "Ireland": "Republic of Ireland",
        "N. Ireland": "Northern Ireland",
        "Papua N. Guinea": "Papua New Guinea",
        "Saint Lucia": "St Lucia",
        "Solomons": "Solomon Islands",
        "St. Kitts/Nevis": "St Kitts and Nevis",
        "St. Vincent": "St Vincent and the Grenadines",
        "São Tomé and P.": "São Tomé and Príncipe",
        "Trinidad": "Trinidad and Tobago",
        "Turkiye": "Türkiye",
        "Turks-Caicos": "Turks and Caicos Islands",
        "UAE": "United Arab Emirates",
        "US Virgin": "US Virgin Islands",
    }
    def __post_init__(self):
        if self.match_type_order is None:
            self.match_type_order = {"f": 0, "q": 1, "t": 2, "w": 3}


db_config= DatabaseConfig()
pipeline_config= PipelineConfig()
