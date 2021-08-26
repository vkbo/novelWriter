## Dictionary Conversion

Source: https://ftp.gnu.org/gnu/aspell/dict/0index.html

```
./configure
make

aspell --dict-dir=. -d en dump master > en.dict
aspell --dict-dir=. -d en_GB-ise-w_accents dump master > en_GB.dict
aspell --dict-dir=. -d en_US-w_accents dump master > en_US.dict
```
