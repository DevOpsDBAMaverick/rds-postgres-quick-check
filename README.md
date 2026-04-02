# rds-postgres-quick-check
A lightweight, zero-overhead Python script to instantly identify the top 5 slowest queries running on your AWS RDS or Aurora PostgreSQL instances.
Instead of digging through AWS CloudWatch logs or navigating the RDS console, this script queries pg_stat_statements directly to show you exactly where your database bottlenecks are.
🚀 Prerequisites
To use this script, your AWS RDS Postgres instance must have the pg_stat_statements extension enabled.
* Go to your AWS RDS Parameter Group.
* Search for shared_preload_libraries.
* Add pg_stat_statements to the list (requires a database reboot if not already enabled).
* Connect to your database and run: CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
🛠️ Installation
* Clone this repository:
git clone https://github.com/your-username/rds-postgres-quick-check.git
cd rds-postgres-quick-check

* Install the required PostgreSQL adapter for Python:
pip install psycopg2-binary

💻 Usage
* Open quick_check.py and update the database connection variables at the top of the file:
DB_HOST = "your-rds-endpoint.amazonaws.com"
DB_NAME = "your_db"
DB_USER = "postgres"
DB_PASS = "your_password"

* Run the script:
python quick_check.py

The script will output the top 5 queries ranked by total execution time, along with execution counts and average runtime in milliseconds.
📄 License
This project is open-source and available under the MIT License.
🤖 Automate Your AWS Performance Fixes
Manual database tuning is a chore. This script is great for ad-hoc checks, but it doesn't solve the underlying problems or prevent CPU spikes.
If you want to move away from manual babysitting and automate your continuous AWS Postgres optimizations, check out www.pgflare.com. It automatically detects and applies performance fixes securely, keeping your database running optimally without the manual headache.
