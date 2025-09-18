-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 18, 2025 at 01:57 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `office_games`
--

-- --------------------------------------------------------

--
-- Table structure for table `housie_numbers`
--

CREATE TABLE `housie_numbers` (
  `id` int(11) NOT NULL,
  `number_drawn` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `housie_numbers`
--

INSERT INTO `housie_numbers` (`id`, `number_drawn`) VALUES
(1, 50),
(2, 30),
(3, 5),
(4, 90),
(5, 76),
(6, 40),
(7, 20);

-- --------------------------------------------------------

--
-- Table structure for table `treasurehunt`
--

CREATE TABLE `treasurehunt` (
  `id` int(11) NOT NULL,
  `hint` text NOT NULL,
  `answer` varchar(255) NOT NULL,
  `answered_by` int(11) DEFAULT 0,
  `hint_shown` int(11) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `treasurehunt`
--

INSERT INTO `treasurehunt` (`id`, `hint`, `answer`, `answered_by`, `hint_shown`) VALUES
(1, 'Go to places of new born where you lived once breathed cherished Stop by the second sentinel standing tall The guardian hides many numbers but only the one wrapped in crimson reveals the way forward', 'LDB01R5', 0, 1),
(2, 'On the second floor where whispers of wisdom linger the library holds your path Search for the shelf whose code is a riddle Double the start double the end and in the middle lies infinitys twin Within its grasp hides a fiery tale find the bird of flame and it will carry you forward', 'DILIB815', 0, 1),
(3, 'Where ideas climb five flights high seek the hall that follows the first of the alphabet There dwells a servant of words it does not speak yet it delivers voices on sacrificial products of Trees The number it bears is the secret you need', 'MNSPLPRN040', 0, 1),
(4, 'I rest where all journeys begin though I move when awoken My skin is the shade of the sky my seat the color of sand I was born in Maharashtra in Second Of February What follows after may be the secret you Need', 'M3401', 0, 1),
(5, 'You In New Territory I stand alone in a crowd of desks my only companion a silent traveler once sent by Amazon Upon me rests a single window to the digital world Yet the secret is not in its screen it hides beneath etched upon the dock that anchors it Who am I', 'MNSPLDOC1375', 0, 1);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `role` varchar(50) NOT NULL,
  `real_name` varchar(100) NOT NULL,
  `profile_photo` varchar(255) DEFAULT NULL,
  `points` int(11) DEFAULT NULL,
  `is_deleted` int(11) NOT NULL DEFAULT 0,
  `gender` varchar(50) NOT NULL DEFAULT 'male'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `role`, `real_name`, `profile_photo`, `points`, `is_deleted`, `gender`) VALUES
(1, 'aman_dua', 'user', 'Aman Dua', 'https://avatar.iran.liara.run/public/30', 0, 0, 'male'),
(2, 'amit_j', 'user', 'Amit J', 'https://avatar.iran.liara.run/public/23', 0, 0, 'male'),
(3, 'prasad_deshmukh', 'user', 'Prasad Deshmukh', 'https://avatar.iran.liara.run/public/15', 0, 0, 'male'),
(4, 'arihant_jain', 'user', 'Arihant Jain', 'https://avatar.iran.liara.run/public/28', 0, 0, 'male'),
(5, 'prafulla_mishra', 'user', 'Prafulla Mishra', 'https://avatar.iran.liara.run/public/50', 0, 0, 'male'),
(6, 'jimit', 'user', 'jimit', 'https://avatar.iran.liara.run/public/20', 0, 0, 'male'),
(7, 'mehul_s', 'user', 'Mehul S', 'https://avatar.iran.liara.run/public/29', 0, 0, 'male'),
(8, 'pravin_h', 'user', 'Pravin H', 'https://avatar.iran.liara.run/public/25', 0, 0, 'male'),
(9, 'mayur_mistry', 'user', 'mayur mistry', 'https://avatar.iran.liara.run/public/36', 0, 0, 'male'),
(10, 'sanskar_khandelwal', 'user', 'Sanskar Khandelwal', 'https://avatar.iran.liara.run/public/22', 0, 0, 'male'),
(11, 'kishan_s', 'user', 'Kishan S', 'https://avatar.iran.liara.run/public/33', 0, 0, 'male'),
(12, 'shivanshu', 'user', 'Shivanshu', 'https://avatar.iran.liara.run/public/44', 0, 0, 'male'),
(13, 'alpesh', 'user', 'Alpesh', 'https://avatar.iran.liara.run/public/1', 0, 0, 'male'),
(14, 'atharva', 'user', 'Atharva', 'https://avatar.iran.liara.run/public/49', 0, 0, 'male'),
(15, 'sujal', 'user', 'Sujal', 'https://avatar.iran.liara.run/public/12', 0, 0, 'male'),
(16, 'madhava_v', 'user', 'Madhava V', 'https://avatar.iran.liara.run/public/10', 0, 0, 'male'),
(17, 'sanket_g', 'user', 'Sanket G', 'https://avatar.iran.liara.run/public/45', 0, 0, 'male'),
(18, 'pratham', 'user', 'Pratham', 'https://avatar.iran.liara.run/public/6', 0, 0, 'male'),
(19, 'parish', 'user', 'Parish', 'https://avatar.iran.liara.run/public/37', 0, 0, 'male'),
(20, 'kanishk', 'user', 'Kanishk', 'https://avatar.iran.liara.run/public/2', 0, 0, 'male'),
(21, 'gaurang_h', 'user', 'Gaurang H', 'https://avatar.iran.liara.run/public/40', 0, 0, 'male'),
(22, 'juan_mathews', 'user', 'Juan Mathews', 'https://avatar.iran.liara.run/public/21', 0, 0, 'male'),
(23, 'rushabh', 'user', 'Rushabh', 'https://avatar.iran.liara.run/public/8', 0, 0, 'male'),
(24, 'vivek', 'user', 'Vivek', 'https://avatar.iran.liara.run/public/43', 0, 0, 'male'),
(25, 'shubham', 'user', 'Shubham', 'https://avatar.iran.liara.run/public/7', 0, 0, 'male'),
(26, 'neeraj', 'user', 'Neeraj', 'https://avatar.iran.liara.run/public/18', 0, 0, 'male'),
(27, 'saket', 'user', 'Saket', 'https://avatar.iran.liara.run/public/16', 0, 0, 'male'),
(28, 'telcy_gomes', 'user', 'Telcy Gomes', 'https://avatar.iran.liara.run/public/80', 0, 0, 'female'),
(29, 'nikita_g', 'user', 'Nikita G', 'https://avatar.iran.liara.run/public/97', 0, 0, 'female'),
(30, 'vijay_n', 'user', 'Vijay N', 'https://avatar.iran.liara.run/public/31', 0, 0, 'male'),
(31, 'avez', 'user', 'Avez', 'https://avatar.iran.liara.run/public/38', 0, 0, 'male'),
(32, 'anmol', 'user', 'Anmol', 'https://avatar.iran.liara.run/public/84', 0, 0, 'female'),
(33, 'shivank', 'admin', 'shivank', 'https://avatar.iran.liara.run/public/14', 0, 0, 'male'),
(34, 'himanshu', 'admin', 'himanshu', 'https://avatar.iran.liara.run/public/46', 80, 0, 'male'),
(35, 'kirit_f', 'user', 'Kirit F', 'https://avatar.iran.liara.run/public/48', 0, 0, 'male'),
(36, 'ramith_n', 'user', 'Ramith N', 'https://avatar.iran.liara.run/public/4', 0, 0, 'male'),
(37, 'govinda.s', 'user', 'Govinda Sharma', 'https://avatar.iran.liara.run/public/2', 0, 0, 'male'),
(38, 'Jojo', 'user', 'Bizzare', 'https://avatar.iran.liara.run/public/9', 0, 0, 'male');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `housie_numbers`
--
ALTER TABLE `housie_numbers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_housie_numbers_id` (`id`);

--
-- Indexes for table `treasurehunt`
--
ALTER TABLE `treasurehunt`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `ix_users_user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `housie_numbers`
--
ALTER TABLE `housie_numbers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `treasurehunt`
--
ALTER TABLE `treasurehunt`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
