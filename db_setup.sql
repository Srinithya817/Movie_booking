CREATE DATABASE IF NOT EXISTS movie_booking;
USE movie_booking;

CREATE TABLE IF NOT EXISTS Customer (
  Cust_id INT AUTO_INCREMENT PRIMARY KEY,
  F_Name VARCHAR(50),
  L_Name VARCHAR(50),
  Email_id VARCHAR(100) UNIQUE,
  Password VARCHAR(255),
  Mobile_no VARCHAR(15),
  DOB DATE,
  Age INT
);

CREATE TABLE IF NOT EXISTS Movie (
  Movie_Id INT AUTO_INCREMENT PRIMARY KEY,
  Movie_Title VARCHAR(100),
  Movie_Description TEXT,
  Movie_Stars VARCHAR(100),
  Language VARCHAR(50),
  Genre VARCHAR(50),
  Rating DECIMAL(2,1) DEFAULT 8.0,
  Duration VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS Movie_Show1 (
  Show_Id INT AUTO_INCREMENT PRIMARY KEY,
  Movie_Id INT,
  Theatre_Name VARCHAR(100),
  City VARCHAR(100),
  Show_Date DATE,
  Show_Time TIME,
  FOREIGN KEY (Movie_Id) REFERENCES Movie(Movie_Id)
);

CREATE TABLE IF NOT EXISTS Booking (
  Booking_Id INT AUTO_INCREMENT PRIMARY KEY,
  Cust_id INT,
  Show_Id INT,
  Seats VARCHAR(200),
  Total_Price DECIMAL(10,2),
  Booking_Ref VARCHAR(20),
  QR_Path VARCHAR(200),
  Booked_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (Show_Id) REFERENCES Movie_Show1(Show_Id)
);

CREATE TABLE IF NOT EXISTS Seat_Lock (
  Lock_Id INT AUTO_INCREMENT PRIMARY KEY,
  Show_Id INT,
  Seat_No VARCHAR(10),
  Booked_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (Show_Id) REFERENCES Movie_Show1(Show_Id)
);

INSERT IGNORE INTO Movie (Movie_Title, Movie_Description, Movie_Stars, Language, Genre, Rating, Duration)
VALUES
('Leo', 'A man with a violent past tries to live peacefully but is pulled back into chaos.', 'Vijay, Trisha', 'Tamil', 'Action', 8.5, '2h 44m'),
('Pushpa 2', 'The story of Pushpa continues as he faces new enemies and becomes a kingpin.', 'Allu Arjun, Rashmika Mandanna', 'Telugu', 'Action', 8.7, '3h 21m'),
('Jawan', 'A man on a mission to right the wrongs of society by taking justice into his own hands.', 'Shah Rukh Khan, Nayanthara', 'Hindi', 'Thriller', 7.9, '2h 49m'),
('Kalki 2898 AD', 'A mythological sci-fi adventure set in a dystopian future.', 'Prabhas, Deepika Padukone', 'Telugu', 'Sci-Fi', 7.2, '2h 59m'),
('Vikram', 'A special task force officer hunts down a group of masked vigilantes.', 'Kamal Haasan, Fahadh Faasil', 'Tamil', 'Action', 8.4, '2h 54m');

INSERT IGNORE INTO Movie_Show1 (Movie_Id, Theatre_Name, City, Show_Date, Show_Time) VALUES
(1, 'PVR Elante Mall', 'Chandigarh', '2026-12-05', '10:00:00'),
(1, 'Cinepolis Bestech Square', 'Chandigarh', '2026-12-05', '14:00:00'),
(1, 'Wave Cinemas', 'Chandigarh', '2026-12-05', '19:00:00'),
(2, 'PVR Elante Mall', 'Chandigarh', '2026-12-05', '09:30:00'),
(2, 'Cinepolis Bestech Square', 'Chandigarh', '2026-12-05', '13:15:00'),
(2, 'Wave Cinemas', 'Chandigarh', '2026-12-05', '18:00:00'),
(3, 'PVR Elante Mall', 'Chandigarh', '2026-12-05', '11:00:00'),
(3, 'Cinepolis Bestech Square', 'Chandigarh', '2026-12-05', '15:30:00'),
(3, 'Wave Cinemas', 'Chandigarh', '2026-12-05', '20:00:00'),
(4, 'PVR Elante Mall', 'Chandigarh', '2026-12-05', '10:15:00'),
(4, 'Cinepolis Bestech Square', 'Chandigarh', '2026-12-05', '15:00:00'),
(4, 'Wave Cinemas', 'Chandigarh', '2026-12-05', '20:30:00'),
(5, 'PVR Elante Mall', 'Chandigarh', '2026-12-05', '12:00:00'),
(5, 'Cinepolis Bestech Square', 'Chandigarh', '2026-12-05', '16:45:00'),
(5, 'Wave Cinemas', 'Chandigarh', '2026-12-05', '21:00:00');
