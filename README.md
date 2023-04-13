# Jar scanner

Scan a list of jar file names (including version number) for vulnerabilities.
The idea is to convert the list to a pom.xml file and scan that using [Owasp Dependency Check](https://owasp.org/www-project-dependency-check/).

## Requirements

Maven
Python
A list of Jar files names

## Usage

    python list_to_pom.py <jarfile_list>
    mvn org.owasp:dependency-check-maven:aggregate
    open target/dependency-check-report.html
