from app import create_app

app = create_app()
# app2 = create_app()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)

    # Here's how to run 2 server instances at the same time from one script
    # from threading import Thread

    # # Start the first Flask app on port 5000
    # def run_app1():
    #     app.run(port=5000)

    # # Start the second Flask app on port 5001
    # def run_app2():
    #     app2.run(port=5001)

    # # Create threads for running both apps simultaneously
    # t1 = Thread(target=run_app1)
    # t2 = Thread(target=run_app2)

    # t1.start()
    # t2.start()

    # t1.join()
    # t2.join()
