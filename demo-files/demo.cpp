#include <iostream>
#include <string>
#include <vector>

// 这是一个C++示例文件
/* 多行注释
   演示语法高亮 */

class DemoClass {
private:
    std::string name;
    int value;

public:
    DemoClass(std::string n, int v) : name(n), value(v) {}

    void printInfo() {
        std::cout << "Name: " << name << ", Value: " << value << std::endl;
    }
};

// TODO: 添加更多功能

int main() {
    const int MAX_COUNT = 100;
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    
    DemoClass demo("测试", 42);
    demo.printInfo();

    return 0;
}