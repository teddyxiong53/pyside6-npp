// Java示例文件
/* 多行注释
   演示语法高亮 */

package com.example.demo;

import java.util.ArrayList;
import java.util.List;

// 接口定义
interface Printable {
    void print();
}

// 类定义
public class DemoClass implements Printable {
    private String name;
    private int value;
    
    public DemoClass(String name, int value) {
        this.name = name;
        this.value = value;
    }
    
    @Override
    public void print() {
        System.out.println("Name: " + name + ", Value: " + value);
    }
    
    // TODO: 添加更多方法
    
    public static void main(String[] args) {
        final int MAX_COUNT = 100;
        List<String> items = new ArrayList<>();
        items.add("测试1");
        items.add("测试2");
        
        DemoClass demo = new DemoClass("示例", 42);
        demo.print();
        
        // 字符串处理
        String message = String.format("当前有 %d 个项目", items.size());
        System.out.println(message);
    }
}