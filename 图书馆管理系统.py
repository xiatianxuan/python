# Copyright © 2025 夏天轩. 版权所有.
# 本代码受《中华人民共和国著作权法》保护，未经书面许可禁止复制、修改或用于商业用途。
# 任何侵权行为将依法追究责任。

import base64 as b
import binascii as bi
import datetime as d
import hashlib as h
import json as js
import secrets as s
from typing import Optional
import os
import sys


class Book:
    def __init__(self, title, author, publisher, isbn, book_id, borrow_time):
        self.title = title
        self.author = author
        self.publisher = publisher
        self.isbn = isbn
        self.id = book_id
        self.borrow = False
        self.borrow_time = borrow_time

    def dict_book(self):
        return {
            "title": self.title,
            "author": self.author,
            "publisher": self.publisher,
            "ISBN": self.isbn,
            "ID": self.id,
            "borrow": self.borrow,
            "borrow_time": self.borrow_time,
        }

    @staticmethod
    def load_book():
        if os.path.exists("books.json"):
            with open("books.json", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return js.loads(content)
        else:
            return []

    @staticmethod
    def save_books(books_list):
        with open("books.json", "w", encoding="utf-8") as f:
            js.dump(books_list, f, ensure_ascii=False, indent=4)

    @staticmethod
    def borrow_book(title, books_list):
        for book in books_list:
            if book["title"] == title:
                if not book["borrow"]:
                    book["borrow"] = True
                    book["borrow_time"] = d.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    return 0
                else:
                    return 1

        return None

    @staticmethod
    def return_book(title, books_list):
        for book in books_list:
            if book["title"] == title:
                if book["borrow"]:
                    book["borrow"] = False
                    book["borrow_time"] = None
                    return 0
                else:
                    return 1

        return None


class User:
    def __init__(self, name, user_id, password, borrow_books_list) -> None:
        self.name = name
        self.id = user_id
        self.password = User.hash_password(password)
        self.borrow_books_list = borrow_books_list

    def dict_user(self) -> dict:
        return {
            "name": self.name,
            "ID": self.id,
            "password": self.password,
            "borrow_books_list": self.borrow_books_list,
        }

    @staticmethod
    def user_login(name, password, users_list):
        for user in users_list:
            if user["name"] == name:
                if User.compare_password(password, user["password"]):
                    return 0
                else:
                    return 1
        return 2

    @staticmethod
    def load_user():
        if os.path.exists("users.json"):
            with open("users.json", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                else:
                    return js.loads(content)
        else:
            return []

    @staticmethod
    def save_users(users_list):
        with open("users.json", "w", encoding="utf-8") as f:
            js.dump(users_list, f, ensure_ascii=False, indent=4)

    @staticmethod
    def borrow_book(title, username, users_list):
        for user in users_list:
            if user["name"] == username:
                if title not in user["borrow_books_list"]:
                    return users_list.index(user)
        return None

    @staticmethod
    def return_book(title, username, users_list):
        for user in users_list:
            if user["name"] == username:
                if title in user["borrow_books_list"]:
                    return users_list.index(user)
        return None

    @staticmethod
    def hash_password(password: str) -> Optional[str]:
        try:
            salt = s.token_bytes(16)
            password = password.encode("utf-8", errors="strict")
            hashPassword = h.pbkdf2_hmac("sha256", password, salt, 200000)
            return b.b64encode(hashPassword + salt).decode()
        except UnicodeError:
            return None

    @staticmethod
    def compare_password(password: str, hash_password: str) -> bool:
        try:
            hash_new = b.b64decode(hash_password.encode())
            if not len(hash_new) == 48:
                return False
            originalPassword = hash_new[:32]
            salt = hash_new[32:]
            if not len(salt) == 16:
                return False
            newHashPassword = h.pbkdf2_hmac(
                "sha256", password.encode("utf-8", errors="strict"), salt, 200000
            )
            return s.compare_digest(newHashPassword, originalPassword)
        except (UnicodeError, bi.Error):
            return False


def append_book(books_list, name, author, publisher, isbn, book_id, borrow_time=None):
    book = Book(
        title=name,
        author=author,
        publisher=publisher,
        isbn=isbn,
        book_id=book_id,
        borrow_time=borrow_time,
    )
    books_list.append(book.dict_book())
    Book.save_books(books_list)


def main():
    while True:
        users_list = User.load_user()
        books_list = Book.load_book()
        print("欢迎使用图书馆管理系统！")
        print("请选择：\n1. 用户登录\n2. 用户注册\n3. 退出系统")
        service = input("请输入你的选择： ")
        if service == "1":
            number = 0
            while True:
                name = input("请输入用户名： ")
                password = input("请输入密码： ")
                if password is None:
                    break
                if User.user_login(name, password, users_list) == 0:
                    print("登录成功！")
                    while True:
                        print("请选择：\n1. 借书\n2. 还书\n3. 添加书籍\n4. 退出系统")
                        choice = input("请输入你的选择： ")
                        if choice == "1":
                            title = input("请输入书名： ")
                            index = User.borrow_book(title, name, users_list)
                            if not index is None:
                                book = Book.borrow_book(title, books_list)
                                if book == 0:
                                    users_list[index]["borrow_books_list"].append(title)
                                    print("借书成功！")
                                    continue
                                elif book is None:
                                    print("未找到此书,借书失败")
                                    continue
                                else:
                                    print(f"{title}已借出，借书失败")
                                    continue

                        elif choice == "2":
                            title = input("请输入要归还的书名： ")
                            index = User.return_book(title, name, users_list)
                            if not index is None:
                                book = Book.return_book(title, books_list)
                                if book == 0:
                                    users_list[index]["borrow_books_list"].remove(title)
                                    print("还书成功！")
                                    continue
                                elif book is None:
                                    print("未找到此书，还书失败")
                                    continue
                                elif book == 1:
                                    print(f"{title}未借出，还书失败")
                                    continue
                            else:
                                print("您并未借阅此书，还书失败")
                                continue
                        elif choice == "4":
                            print("感谢使用图书管理系统！")
                            User.save_users(users_list)
                            Book.save_books(books_list)
                            sys.exit()
                        elif choice == "3":
                            bookname = input("请输入书名： ")
                            author = input("请输入作者： ")
                            publisher = input("请输入出版社： ")
                            isbn = input("请输入ISBN： ")
                            if not books_list:
                                book_id = 1
                            else:
                                book_id = books_list[-1]["ID"] + 1

                            append_book(
                                books_list, bookname, author, publisher, isbn, book_id
                            )
                            books_list = Book.load_book()
                            print("添加成功！")
                            continue
                        else:
                            print("无效的选择，请重新选择。")
                            continue
                elif User.user_login(name, password, users_list) == 1:
                    print("密码错误！, 请检查后再次输入。")
                    number += 1
                else:
                    print("用户不存在，请先注册或检查用户名.")
                    break
                if number == 3:
                    print("尝试次数过多，请检查用户名和密码后再试")
                    sys.exit()
        elif service == "2":
            number = 0
            while True:
                name = input("请输入要注册的用户名(用户名最大4位)： ")
                password = input("请设置密码(密码必须是6位数字)： ")
                if password.isdigit() and len(password) == 6 and len(name) <= 4:
                    if users_list:
                        user = User(name, users_list[-1]["ID"] + 1, password, [])
                        users_list.append(user.dict_user())
                        User.save_users(users_list)
                        print("注册成功！请重新登录。")
                        break
                    else:
                        user = User(name, 1, password, [])
                        users_list.append(user.dict_user())
                        User.save_users(users_list)
                        print("注册成功！请重新登录。")
                        break
                elif number == 3:
                    print("尝试次数过多，请检查用户名和密码后再试")
                    break
                else:
                    print("注册失败！请检查用户名、密码是否符合要求。")
                    number += 1
                    continue
        elif service == "3":
            print("感谢使用图书馆管理系统！")
            Book.save_books(books_list)
            User.save_users(users_list)
            sys.exit()
        else:
            print("无效输入，请重新选择")


if __name__ == "__main__":
    main()
