SELECT 'CREATE DATABASE campuspulse_auth' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'campuspulse_auth')\gexec
SELECT 'CREATE DATABASE campuspulse_feedback' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'campuspulse_feedback')\gexec
SELECT 'CREATE DATABASE campuspulse_notifications' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'campuspulse_notifications')\gexec
SELECT 'CREATE DATABASE campuspulse_assistant' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'campuspulse_assistant')\gexec
