import csv
import os
import shutil
import subprocess
import sys
import urllib.request

JAVA_PATH = "java"


def get_info_for_files(filename: str):
    with open(filename) as urls_file:
        urls = [u.strip() for u in urls_file.readlines() if u]
    return [u.strip().split(' ') for u in urls if u]


def get_java_process(command_parts, is_error_piped):
    return subprocess.Popen(command_parts,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE if is_error_piped else subprocess.STDOUT,
                            shell=False)


def save_results(lines):
    if os.getcwd().endswith('jar_test'):
        os.chdir('..')
    with open("linux.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows([["JAR", "error"]])
        writer.writerows(lines)
    print(f'Errors count: {len([x for x in lines if x[1]])}')


def main():
    results = []
    urls = get_info_for_files(sys.argv[1])
    total = len(urls)
    for i, url in enumerate(urls, 1):
        # prepare the folders
        if os.getcwd().endswith('jar_test'):
            os.chdir('..')
        if os.path.exists("jar_test"):
            shutil.rmtree("jar_test")
        os.makedirs("jar_test")
        os.chdir("jar_test")

        # download the file
        link, jar_name = url[0], url[1]
        print(f'[{i}/{total}] downloading {link} as {jar_name}')
        try:
            urllib.request.urlretrieve(link, jar_name)
        except:
            error_message = f'Could not download the JAR file from {link}'
            print(error_message)
            results.append([str(jar_name), error_message])
            os.chdir('..')
            continue

        # run the JAR; if doesn't terminate within a few seconds, assume the UI launched successfully
        java_process = get_java_process([JAVA_PATH, "-jar", jar_name], is_error_piped=False)
        try:
            java_process.wait(5)
        except subprocess.TimeoutExpired:
            print("Ok")
            java_process.kill()
            results.append([jar_name, ''])
            continue

        # run once more, to weed out 'crashes only first time' cases
        java_process = get_java_process([JAVA_PATH, "-jar", jar_name], is_error_piped=False)
        try:
            java_process.wait(5)
        except subprocess.TimeoutExpired:
            java_process.kill()
            results.append([jar_name, 'Observation: crashed the first time, but not the second time'])
            continue

        # if crashed both times, run again to collect the error message
        java_process = get_java_process([JAVA_PATH, "-jar", jar_name], is_error_piped=True)
        status_message = java_process.communicate()[1]
        print(status_message)
        java_process.kill()
        results.append([str(jar_name), str(status_message)])

    save_results(results)


if __name__ == '__main__':
    main()
