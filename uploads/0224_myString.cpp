#include <iostream>
#include <string.h>
#include <stdlib.h>

using namespace std;

class MyString
{
private:
    char *_pData;
    int _size;
public:
    MyString();
    MyString(const char *);
    MyString(const MyString &);
    ~MyString();
    MyString& operator=(const MyString &);
    friend ostream &operator<<(ostream &out, const MyString str);
    int size();
};

MyString::MyString() {
    _pData = NULL;
}
MyString::MyString(const char *str) {
    if (str == NULL)
        return ;
    _size = strlen(str);
    _pData = (char*)malloc(_size+1);
    memcpy(_pData, str, _size+1);
}
MyString::MyString(const MyString &str) {
    if (str._pData) {
        _size = str._size;
        _pData = (char *)malloc(_size+1);
        memcpy(_pData, str._pData, _size+1);
    }
}
MyString::~MyString() {
    free(_pData);
}
MyString& MyString::operator=(const MyString &str) {
    if (this != &str) {
        MyString strTemp(str);
        char *pTemp = strTemp._pData;
        strTemp._pData = _pData;
        _pData = pTemp;
        _size = strTemp._size;
    }
    return *this;
}
ostream &operator<<(ostream &out, const MyString str) {
    out << str._pData;
    return out;
}
int MyString::size() {
    return _size;
}


int main(int argc, const char *argv[])
{
    MyString str1("111");
    MyString str2(str1);
    MyString str3 = str2 = str1;

    cout << str1 << endl;
    cout << str2 << endl;
    cout << str3 << endl;
    std::cout << "size ==> " << str3.size() << std::endl;
    return 0;
}
