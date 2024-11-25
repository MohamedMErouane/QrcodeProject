
        # Connect to the SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.set_debuglevel(1)  # Enables debug output to check SMTP session
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        print("Absence notification sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        print("SMTP Authentication Error: Please check the app password and account settings.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Example usage:
absentees = ["John Doe", "Jane Smith", "Mark