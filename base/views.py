from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import GlucoseReading
from django.utils.dateparse import parse_datetime
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .models import GlucoseReading

from .forms import RegisterForm
from .models import GlucoseReading, Chat
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import matplotlib.pyplot as plt
from .models import GlucoseReading
from django.conf import settings
import openai
from django.core.cache import cache

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import GlucoseReading

from .forms import RegisterForm, MealLogForm  # Add MealLogForm
from .models import GlucoseReading, Meal, Food  # Add Food model
from .forms import RegisterForm, MealLogForm  # Add MealLogForm

from django.shortcuts import render
from .models import GlucoseReading

@login_required
def glucose_reading_list(request):
    if request.method == 'GET':
        readings = GlucoseReading.objects.filter(user=request.user)
        return render(request, 'base/glucose_readings_list.html', {'readings': readings})

    elif request.method == 'POST':
        reading = request.POST.get('reading')
        date_time_str = request.POST.get('date_time')
        reading_type = request.POST.get('reading_type')  # Capture reading_type

        date_time = parse_datetime(date_time_str)

        if reading and date_time:
            GlucoseReading.objects.create(
                user=request.user,
                reading=reading,
                date_time=date_time,
                reading_type=reading_type  # Pass the reading_type
            )
        return redirect('glucose_reading_success') 
       
@login_required
def glucose_reading_success(request):
    last_reading = GlucoseReading.objects.filter(user=request.user).last()

    if last_reading:
        reading_value = last_reading.reading
        if reading_value >= 126:
            message = "The person is diabetic, he or she should see a doctor."
        elif 100 <= reading_value < 126:
            message = "Your glucose reading is above 100 mg/dl. You should make some changes in your lifestyle and consider seeing a doctor."
        else:
            message = "Glucose level is normal."
    else:
        message = "No recent reading found."

    return render(request, 'base/glucose_reading_success.html', {'message': message})

#Previous reading
@login_required
def previous_readings(request):
    # Your existing view logic
    readings_before_eating = GlucoseReading.objects.filter(user=request.user, reading_type=GlucoseReading.BEFORE_EATING)
    readings_after_eating = GlucoseReading.objects.filter(user=request.user, reading_type=GlucoseReading.AFTER_EATING)

    context = {
        'readings_before_eating': readings_before_eating,
        'readings_after_eating': readings_after_eating,
    }

    # If download_pdf parameter is present, generate and return the PDF
    if 'download_pdf' in request.GET:
        return generate_pdf('base/pdf_template.html', context, filename="My_Glucose_History.pdf")

    # Your existing code for rendering the HTML template
    return render(request, 'base/previous_readings.html', context)

def generate_pdf(template_path, context, filename="output.pdf"):
    # Render the PDF template
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))

    return response


@login_required
def glucose_reading_graph(request, reading_type='all'):
    # Filter readings based on type
    if reading_type == 'before':
        readings = GlucoseReading.objects.filter(user=request.user, reading_type='before').order_by('date_time')
    elif reading_type == 'after':
        readings = GlucoseReading.objects.filter(user=request.user, reading_type='after').order_by('date_time')
    else:
        readings = GlucoseReading.objects.filter(user=request.user).order_by('date_time')

    # Prepare data
    dates = [reading.date_time.strftime("%Y-%m-%d %H:%M") for reading in readings]
    values = [reading.reading for reading in readings]  # Assuming 'reading_value' holds the glucose value

    # Create a Matplotlib figure
    fig, ax = plt.subplots()
    ax.plot(dates, values)
    title = 'Glucose Readings After Eating' if reading_type == 'after' else 'Glucose Readings Before Eating' if reading_type == 'before' else 'All Glucose Readings'
    ax.set(title=title, xlabel='Date', ylabel='Reading (mg/dL)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the figure
    fig_filename = f'glucose_graph_{reading_type}.png'
    fig_path = os.path.join(settings.BASE_DIR, 'static', 'images', fig_filename)
    fig.savefig(fig_path)
    plt.close(fig)  # Close the plot to free up memory

    # Context for template
    context = {
        'graph_image_url': f'/static/images/{fig_filename}',
        'reading_type': reading_type
              }

    return render(request, 'base/glucose_reading_graph.html', context)

def view_meal_plan(request):
    # Fetch the latest glucose reading for the user
    last_reading = GlucoseReading.objects.filter(user=request.user).last()

    # Default values for glucose level, meal suggestions, and image path
    glucose_level = None
    meal_suggestions = []
    image_path = None

    if last_reading:
        glucose_level = last_reading.reading

        # Determine meal suggestions based on glucose level
        if glucose_level >= 126:
            meal_suggestions.append("Consult with a doctor for a personalized meal plan.")
        elif 100 <= glucose_level < 126:
            meal_suggestions.append("Consider making lifestyle changes and consult with a doctor.")
        else:
            meal_suggestions.append("Your glucose level is within the normal range.")

        # Set the image path based on glucose level
        if glucose_level < 100:
            image_path = 'images/normal_glucose.png'
        elif 100 <= glucose_level < 126:
            image_path = 'images/normal_glucose.png'
        else:
            image_path = 'images/diabetic_glucose.png'

    context = {
        'glucose_level': glucose_level,
        'meal_suggestions': meal_suggestions,
        'image_path': image_path,
    }

    return render(request, 'base/view_meal_plan.html', context)
def login_view(request):
    return auth_views.LoginView.as_view(template_name='base/login.html')(request)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # You can also log the user in and redirect them to another page
            return redirect('login')  # Redirect to login page after registration
    else:
        form = RegisterForm()
    return render(request, 'base/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout

open_api_key = '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'
openai.api_key = open_api_key

def ask_openai(message):
    
    response = openai.Completion.create(
        model = "gpt-3.5-turbo-instruct",
        prompt = message,
        max_tokens = 150,
        n = 1,
        stop = None,
        temperature = 0.7,
    )
    answer = response.choices[0].text.strip()
    return answer

from django.http import JsonResponse
import traceback

def chatbot(request):
    try:
        if request.method == 'POST':
            message = request.POST.get('message')
            response = ask_openai(message)
            chat = Chat(message=message, response=response)
            chat.save()
            return JsonResponse({'message': message, 'response': response})
        else:
            return render(request, 'base/chatbot.html')
    except Exception as e:
        traceback.print_exc()  # Prints the stack trace to the console
        return JsonResponse({'error': str(e)}, status=500)


