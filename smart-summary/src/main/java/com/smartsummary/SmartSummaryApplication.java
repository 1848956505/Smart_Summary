package com.smartsummary;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.smartsummary.repository")
public class SmartSummaryApplication {
    public static void main(String[] args) {
        SpringApplication.run(SmartSummaryApplication.class, args);
    }
}