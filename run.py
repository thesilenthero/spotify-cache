from playlist import update

if __name__ == '__main__':
    try:
        update()
    except Exception as e:
        input(e)
