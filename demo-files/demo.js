// JavaScript示例文件
/* 多行注释
   演示语法高亮 */

// ES6 类定义
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }

    sayHello() {
        console.log(`你好，我是 ${this.name}`);
    }
}

// 箭头函数
const calculateSum = (a, b) => a + b;

// 模板字符串和字符串操作
const greeting = 'Hello';
const world = "World";
const message = `${greeting} ${world}!`;

// TODO: 添加更多示例

// 异步函数示例
async function fetchData() {
    try {
        const response = await fetch('https://api.example.com/data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// 对象和数组操作
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(num => num * 2);

const person = new Person('张三', 25);
person.sayHello();