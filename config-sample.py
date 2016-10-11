# Virtualenv location
VENV_PATH = '/path/to/venv'

# Debug mode
DEBUG = False

# Log mode
LOG = False

# Log file location
LOGFILE = '/path/to/log'

# Secret key for session management
SECRET_KEY = 'xxxxxx'

# Database settings
SQLALCHEMY_DATABASE_URI = 'mysql://user:password/database'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Google client ID
GOOGLE_CLIENT_ID = ''

# Perseids client ID
PERSEIDS_CLIENT_ID = ''

# Perseids client secret
PERSEIDS_CLIENT_SECRET = ''

# Perseids redirect uri
PERSEIDS_REDIRECT_URI = ''

# Hand metadata fields
METADATA_VALUES = {
    'meta_handwriting_professional': [
        ('', ''),
        ('unknown', 'Not known'),
        ('non_professional', 'Non-professional'),
        ('professional', 'Professional'),
        ('practiced', 'Practised letterhand')
    ], 'meta_text_type': [
        ('',''),
        ('letter', 'Letter'),
        ('letter_private', 'Private letter'),
        ('letter_official', 'Official letter'),
        ('letter_business', 'Business letter'),
        ('letter_recommendation', 'Recommendation letter'),
        ('SEPARATOR', '-----'),
        ('contract', 'Contract'),
        ('contract_sale', 'Sale contract'),
        ('contract_loan', 'Loan contract'),
        ('contract_marriage', 'Marriage or divorce contract'),
        ('contract_donation', 'Donation contract'),
        ('contract_work', 'Work contract'),
        ('SEPARATOR', '-----'),
        ('testament', 'Testament'),
        ('petition', 'Petition'),
        ('SEPARATOR', ''),
        ('account', 'Account'),
        ('account_receipt', 'Receipt'),
        ('account_payment', 'Payment order'),
        ('account_bank', 'Bank and taxation'),
        ('SEPARATOR', '-----'),
        ('list', 'List'),
        ('SEPARATOR', '-----'),
        ('belief_superstition', 'Belief or superstition'),
        ('belief_superstition_dream', 'Dream description'),
        ('belief_superstition_oracle', 'Oracle question'),
        ('belief_superstition_mummy_label', 'Mummy label'),
        ('SEPARATOR', '-----'),
        ('signature_subscription', 'Signature or subscription'),
        ('military', 'Military document'),
        ('other', 'Other'),
    ], 'meta_addressee': [
        ('', ''),
        ('unknown', 'Not known or applicable'),
        ('official', 'Official'),
        ('private', 'Private'),
    ]
}