import csv
import os
import shutil
import subprocess
import sys
import urllib.request

JAVA_PATH = "java"
results = []


def get_info_for_files(filename: str):
    with open(filename) as urls_file:
        urls = [u.strip() for u in urls_file.readlines() if u]
    return [u for u in urls if u]


def get_java_process(command_parts, is_error_piped):
    return subprocess.Popen(command_parts,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE if is_error_piped else subprocess.STDOUT,
                            shell=False)


def main():
    # read URLs
    urls = get_info_for_files(sys.argv[1])
    total = len(urls)
    for i, url in enumerate(urls, 1):
        # download the JAR file
        link, jar_name = url.strip().split(' ')
        print(f'[{i}/{total}] downloading {link} as {jar_name}')
        try:
            os.chdir("jars")
            urllib.request.urlretrieve(link, jar_name)
        except:
            error_message = f'Could not download the JAR file from {link}'
            print(error_message)
            results.append([str(jar_name), error_message])
            continue
        finally:
            os.chdir('..')

        # prepare to run the JAR file
        jar_path = os.path.join(os.getcwd(), 'jars', jar_name)
        if not os.path.exists("jar_test"):
            os.makedirs("jar_test")
        shutil.copy2(jar_path, "jar_test")
        os.chdir("jar_test")
        is_ok = False
        status_message = ''

        # run the JAR; if doesn't terminate within a few seconds, assume the UI launched successfully
        java_process = get_java_process([JAVA_PATH, "-jar", jar_name], is_error_piped=False)

        try:
            java_process.wait(5)
        except subprocess.TimeoutExpired:
            print("Ok")
            java_process.kill()
            is_ok = True
        if is_ok:
            status_message = ""
        else:
            # run once more, to weed out 'crashes only first time' cases
            java_process = get_java_process([JAVA_PATH, "-jar", jar_name], is_error_piped=False)
            try:
                java_process.wait(5)
            except subprocess.TimeoutExpired:
                java_process.kill()
                is_ok = True
                status_message = 'Observation: crashed the first time, but not the second time'

            # Crashed both times. Run again to collect the error message
            if not is_ok:
                java_process = get_java_process([JAVA_PATH, "-jar", jar_name], is_error_piped=True)
                status_message = java_process.communicate()[1]
                print(status_message)
                java_process.kill()

        # record the result
        results.append([str(jar_name), str(status_message)])

        # clen up
        os.remove(jar_path)
        os.chdir("..")
        shutil.rmtree("jar_test")

    with open("linux.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows([["JAR", "error"]])
        writer.writerows(results)

    print(f'Errors count: {len([x for x in results if x[1]])}')


if __name__ == '__main__':
    main()
