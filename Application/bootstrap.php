<?php
require_once 'common.php';

function doBootstrap($isWebUI = False) {

	$errors = array();
	# link to tmp_name for proper read address
	$zip_file = $_FILES["bootstrap-file"]["tmp_name"];

	# Get temp dir on system for uploading
	$temp_dir = sys_get_temp_dir();

	# keep track of number of lines successfully processed for each file
	$num_record_loaded = array();
	$student_processed=0;
	$course_processed=0;
	$section_processed=0;
	$prerequisite_processed=0;
	$course_completed_processed=0;
	$bid_processed=0;

	#keep track of the errors per type
	$student_errors = array();
	$course_errors = array();
	$section_errors = array();
	$prerequisite_errors = array();
	$course_completed_errors = array();
	$bid_errors = array();
	

	# check file size
	if ($_FILES["bootstrap-file"]["size"] <= 0)
		$errors[] = "input files not found";

	else {
		
		$zip = new ZipArchive;
		$res = $zip->open($zip_file);

		if ($res === TRUE) {
			$zip->extractTo($temp_dir);
			$zip->close();
		
			$student_path = "$temp_dir/student.csv";
			$course_path = "$temp_dir/course.csv";
			$section_path = "$temp_dir/section.csv";
			$prerequisite_path = "$temp_dir/prerequisite.csv";
			$course_completed_path = "$temp_dir/course_completed.csv";
			$bid_path = "$temp_dir/bid.csv";
			
			#open the "file windows" of the csv files
			$student_file = @fopen($student_path, "r");
			$course_file = @fopen($course_path, "r");
			$section_file = @fopen($section_path, "r");
			$prerequisite_file = @fopen($prerequisite_path, "r");
			$course_completed_file = @fopen($course_completed_path, "r");
			$bid_file = @fopen($bid_path, "r");
			
			if (empty($student_file) || empty($course_file) || empty($section_file) || empty($prerequisite_file) || empty($course_completed_file) || empty($bid_file)){
				$errors[] = "input files not found";
				if (!empty($student_file)){
					fclose($student_file);
					@unlink($student_path);
				} 
				
				if (!empty($course_file)) {
					fclose($course_file);
					@unlink($course_path);
				}
				
				if (!empty($section_file)) {
					fclose($section_file);
					@unlink($section_path);
				}

				if (!empty($prerequisite_file)){
					fclose($prerequisite_file);
					@unlink($prerequisite_path);
				} 

				if (!empty($course_completed_file)){
					fclose($course_completed_file);
					@unlink($course_completed_path);
				} 

				if (!empty($bid_file)){
					fclose($bid_file);
					@unlink($bid_path);
				} 
				
				
			}
			else {

				# start processing
				$StudentDAO = new StudentDAO();
				$CourseDAO = new CourseDAO();
				$SectionDAO = new SectionDAO();
				$PrerequisiteDAO = new PrerequisiteDAO();
				$CourseCompletedDAO = new CourseCompletedDAO();
				$BidDAO = new BidDAO();
				$RoundDAO = new RoundDAO();
				$BidHistoryDAO = new BidHistoryDAO();
				$SectionStudentDAO = new SectionStudentDAO();

				# truncate current SQL tables
				$StudentDAO->removeAll();
				$CourseDAO->removeAll();
				$SectionDAO->removeAll();
				$PrerequisiteDAO->removeAll();
				$CourseCompletedDAO->removeAll();
				$BidDAO->removeAll();
				$BidHistoryDAO->removeAll();
				$RoundDAO->removeAll();
				$SectionStudentDAO->removeAll();

				# reset round values
				$RoundDAO->resetRounds();

				// Student skip header
				$student_header = fgetcsv($student_file);
				$student_line = 1;
				
				// process each line, check for errors, then insert if no errors
				while (($row = fgetcsv($student_file)) !== false) {
					$student_line++;
					$row_error = array();
					$row = trim_row($row);
					$isBlank = isBlank($row);

					if ($isBlank != []) {
						foreach ($isBlank as $i) {
							$row_error[] = "blank $student_header[$i]";
						}
						// $errors[] = ["file" => "student.csv", "line" => $student_line, "message" => $row_error];
						$student_errors[] = ["file" => "student.csv", "line" => $student_line, "message" => $row_error];
						continue;
					}

					$student = new Student($row[0], $row[1], $row[2], $row[3], $row[4]);

					$student_result = $StudentDAO->add($student);

					if ($student_result !== TRUE) {
						// $errors[] = ["file" => "student.csv", "line" => $student_line, "message" => $student_result];
						$student_errors[] = ["file" => "student.csv", "line" => $student_line, "message" => $student_result];
						continue;
					}

					$student_processed++;
					
				}
				
				// clean up
				fclose($student_file);
				@unlink($student_path);	


				// Course skip header
				$course_header = fgetcsv($course_file);
				$course_line = 1;
				
				// process each line, check for errors, then insert if no errors
				while (($row = fgetcsv($course_file)) !== false) {
					$course_line++;
					$row_error = array();
					$row = trim_row($row);
					$isBlank = isBlank($row);

					if ($isBlank != []) {
						foreach ($isBlank as $i) {
							$row_error[] = "blank $course_header[$i]";
						}
						// $errors[] = ["file" => "course.csv", "line" => $course_line, "message" => $row_error];
						$course_errors[] = ["file" => "course.csv", "line" => $course_line, "message" => $row_error];
						continue;
					}
					
					$course = new Course($row[0], $row[1], $row[2], $row[3], $row[4], $row[5], $row[6]);

					$course_result = $CourseDAO->add($course);

					if ($course_result !== TRUE) {
						// $errors[] = ["file" => "course.csv", "line" => $course_line, "message" => $course_result];
						$course_errors[] = ["file" => "course.csv", "line" => $course_line, "message" => $course_result];
						continue;
					}

					$course_processed++;
					
				}
				
				// clean up
				fclose($course_file);
				@unlink($course_path);


				// Section skip header
				$section_header = fgetcsv($section_file);
				$section_line = 1;
				
				// process each line, check for errors, then insert if no errors
				while (($row = fgetcsv($section_file)) !== false) {
					$section_line++;
					$row_error = array();
					$row = trim_row($row);
					$isBlank = isBlank($row);

					if ($isBlank != []) {
						foreach ($isBlank as $i) {
							$row_error[] = "blank $section_header[$i]";
						}
						// $errors[] = ["file" => "section.csv", "line" => $section_line, "message" => $row_error];
						$section_errors[] = ["file" => "section.csv", "line" => $section_line, "message" => $row_error];
						continue;
					}
					
					$section = new Section($row[0], $row[1], $row[2], $row[3], $row[4], $row[5], $row[6], $row[7], "10");

					#var_dump($section);

					$section_result = $SectionDAO->add($section);

					if ($section_result !== TRUE) {
						// $errors[] = ["file" => "section.csv", "line" => $section_line, "message" => $section_result];
						$section_errors[] = ["file" => "section.csv", "line" => $section_line, "message" => $section_result];
						continue;
					}

					$section_processed++;
					
				}
				
				// clean up
				fclose($section_file);
				@unlink($section_path);
				

				// Prerequisite skip header
				$prerequisite_header = fgetcsv($prerequisite_file);
				$prerequisite_line = 1;
				
				// process each line, check for errors, then insert if no errors
				while (($row = fgetcsv($prerequisite_file)) !== false) {
					$prerequisite_line++;
					$row_error = array();
					$row = trim_row($row);
					$isBlank = isBlank($row);

					if ($isBlank != []) {
						foreach ($isBlank as $i) {
							$row_error[] = "blank $prerequisite_header[$i]";
						}
						// $errors[] = ["file" => "prerequisite.csv", "line" => $prerequisite_line, "message" => $row_error];
						$prerequisite_errors[] = ["file" => "prerequisite.csv", "line" => $prerequisite_line, "message" => $row_error];
						continue;
					}
					
					$prerequisite = new Prerequisite($row[0], $row[1]);

					$prerequisite_result = $PrerequisiteDAO->add($prerequisite);

					if ($prerequisite_result !== TRUE) {
						// $errors[] = ["file" => "prerequisite.csv", "line" => $prerequisite_line, "message" => $prerequisite_result];
						$prerequisite_errors[] = ["file" => "prerequisite.csv", "line" => $prerequisite_line, "message" => $prerequisite_result];
						continue;
					}

					$prerequisite_processed++;
					
				}
				
				// clean up
				fclose($prerequisite_file);
				@unlink($prerequisite_path);


				// CourseCompleted skip header
				$course_completed_header = fgetcsv($course_completed_file);
				$course_completed_line = 1;

				// process each line, check for errors, then insert if no errors
				while (($row = fgetcsv($course_completed_file)) !== false) {
					$course_completed_line++;
					$row_error = array();
					$row = trim_row($row);
					$isBlank = isBlank($row);

					if ($isBlank != []) {
						foreach ($isBlank as $i) {
							$row_error[] = "blank $course_completed_header[$i]";
						}
						// $errors[] = ["file" => "course_completed.csv", "line" => $course_completed_line, "message" => $row_error];
						$course_completed_errors[] = ["file" => "course_completed.csv", "line" => $course_completed_line, "message" => $row_error];
						continue;
					}

					$courseCompleted = new CourseCompleted($row[0], $row[1]);

					$course_completed_result = $CourseCompletedDAO->add($courseCompleted);

					if ($course_completed_result !== TRUE) {
						// $errors[] = ["file" => "course_completed.csv", "line" => $course_completed_line, "message" => $course_completed_result];
						$course_completed_errors[] = ["file" => "course_completed.csv", "line" => $course_completed_line, "message" => $course_completed_result];
						continue;
					}

					$course_completed_processed++;
					
				}
				
				// clean up
				fclose($course_completed_file);
				@unlink($course_completed_path);

				// Bid skip header
				$bid_header = fgetcsv($bid_file);
				$bid_line = 1;
				
				// process each line, check for errors, then insert if no errors
				while (($row = fgetcsv($bid_file)) !== false) {
					$bid_line++;
					$row_error = array();
					$row = trim_row($row);
					$isBlank = isBlank($row);

					if ($isBlank != []) {
						foreach ($isBlank as $i) {
							$row_error[] = "blank $bid_header[$i]";
						}
						// $errors[] = ["file" => "bid.csv", "line" => $bid_line, "message" => $row_error];
						$bid_errors[] = ["file" => "bid.csv", "line" => $bid_line, "message" => $row_error];
						continue;
					}
					
					$bid = new Bid($row[0], $row[1], $row[2], $row[3], "-");

					$bid_result = $BidDAO->add($bid);

					if ($bid_result !== TRUE) {
						// $errors[] = ["file" => "bid.csv", "line" => $bid_line, "message" => $bid_result];
						$bid_errors[] = ["file" => "bid.csv", "line" => $bid_line, "message" => $bid_result];
						continue;
					}

					$bid_processed++;
					
				}
				
				// clean up
				fclose($bid_file);
				@unlink($bid_path);

			}
		}
	}
	

	# Return JSON format errors. remember this is only for the JSON API. Humans should not get JSON errors.

	$num_record_loaded[] = ["bid.csv" => $bid_processed];
	$num_record_loaded[] = ["course.csv" => $course_processed];
	$num_record_loaded[] = ["course_completed.csv" => $course_completed_processed];
	$num_record_loaded[] = ["prerequisite.csv" => $prerequisite_processed];
	$num_record_loaded[] = ["section.csv" => $section_processed];
	$num_record_loaded[] = ["student.csv" => $student_processed];

	$errorList = ["bid_errors", "course_errors", "course_completed_errors", "prerequisite_errors", "section_errors", "student_errors"];

	$hasError = False;

	foreach ($errorList as $errorTitle) {
		if (!empty(${$errorTitle})) {
			$hasError = True;

			foreach (${$errorTitle} as $errorItem) {
				$errors[] = $errorItem;
			}
		}
	}

	if ($hasError) # !isEmpty($errors)
	{	
		// $sortclass = new Sort();
		// $errors = $sortclass->sort_it($errors,"bootstrap");

		$result = [ 
			"status" => "error",
			"num-record-loaded" => $num_record_loaded,
			"error" => $errors
		];
	} else {	
		$result = [ 
			"status" => "success",
			"num-record-loaded" => $num_record_loaded
				// "bid.csv" => $bid_processed,
				// "course.csv" => $course_processed,
				// "course_completed.csv" => $course_completed_processed,
				// "prerequisite.csv" => $prerequisite_processed,
				// "section.csv" => $section_processed,
				// "student.csv" => $student_processed
		];
	}

	if ($isWebUI) {
		return $result;
	}

	header('Content-Type: application/json');
	echo json_encode($result, JSON_PRETTY_PRINT);

}
?>