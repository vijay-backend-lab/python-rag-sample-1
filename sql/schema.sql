CREATE TABLE IF NOT EXISTS study (
  study_id VARCHAR(64) PRIMARY KEY, study_name VARCHAR(255) NOT NULL,
  protocol_number VARCHAR(100), phase VARCHAR(30), therapeutic_area VARCHAR(100),
  status VARCHAR(30), sponsor VARCHAR(255), start_date DATE,
  planned_end_date DATE, actual_end_date DATE, target_enrollment INT
);
CREATE TABLE IF NOT EXISTS site (
  site_id VARCHAR(64) PRIMARY KEY, study_id VARCHAR(64) NOT NULL,
  site_name VARCHAR(255) NOT NULL, country VARCHAR(100), region VARCHAR(100),
  status VARCHAR(30), activation_date DATE, close_date DATE, target_enrollment INT,
  FOREIGN KEY (study_id) REFERENCES study(study_id)
);
CREATE TABLE IF NOT EXISTS investigator (
  investigator_id VARCHAR(64) PRIMARY KEY, site_id VARCHAR(64) NOT NULL,
  name VARCHAR(255), role VARCHAR(100), active BOOLEAN,
  FOREIGN KEY (site_id) REFERENCES site(site_id)
);
CREATE TABLE IF NOT EXISTS recruitment_assignment (
  assignment_id VARCHAR(64) PRIMARY KEY, site_id VARCHAR(64) NOT NULL,
  person_id VARCHAR(64), recruitment_role VARCHAR(100), start_date DATE, end_date DATE,
  FOREIGN KEY (site_id) REFERENCES site(site_id)
);
CREATE TABLE IF NOT EXISTS participant (
  participant_id VARCHAR(64) PRIMARY KEY, study_id VARCHAR(64) NOT NULL,
  site_id VARCHAR(64) NOT NULL, status VARCHAR(30), screening_date DATE,
  enrollment_date DATE, randomization_date DATE, completion_date DATE, withdrawal_date DATE,
  FOREIGN KEY (study_id) REFERENCES study(study_id), FOREIGN KEY (site_id) REFERENCES site(site_id)
);
CREATE TABLE IF NOT EXISTS milestone (
  milestone_id VARCHAR(64) PRIMARY KEY, study_id VARCHAR(64) NOT NULL,
  site_id VARCHAR(64), milestone_type VARCHAR(100), planned_date DATE,
  actual_date DATE, status VARCHAR(30), FOREIGN KEY (study_id) REFERENCES study(study_id),
  FOREIGN KEY (site_id) REFERENCES site(site_id)
);
CREATE TABLE IF NOT EXISTS issue (
  issue_id VARCHAR(64) PRIMARY KEY, study_id VARCHAR(64) NOT NULL,
  site_id VARCHAR(64), issue_type VARCHAR(100), severity VARCHAR(30), status VARCHAR(30),
  opened_date DATE, closed_date DATE, FOREIGN KEY (study_id) REFERENCES study(study_id),
  FOREIGN KEY (site_id) REFERENCES site(site_id)
);
CREATE INDEX idx_participant_enrollment ON participant(study_id, site_id, enrollment_date);
CREATE INDEX idx_site_location ON site(study_id, country, region);

