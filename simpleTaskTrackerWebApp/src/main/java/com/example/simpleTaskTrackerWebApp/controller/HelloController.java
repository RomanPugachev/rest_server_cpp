package com.example.simpleTaskTrackerWebApp.controller;

import com.example.simpleTaskTrackerWebApp.utils.StringGenerator;
import static com.example.simpleTaskTrackerWebApp.utils.WordsGenerator.*;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {
    @GetMapping("/")
    public String hello() {
        StringGenerator stringGenerator = new StringGenerator();
        return "Welcome to brand new greeting page, built from Git Actions!\n\n\n"
                + "Here is a random string: " + stringGenerator.generateRandomString(10) + "\n\n\n"
                + "Here is sentence of 10 words: " + generateRandomSentence(10);
    }
}